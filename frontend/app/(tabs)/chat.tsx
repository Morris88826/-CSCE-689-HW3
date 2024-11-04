import { Ionicons } from "@expo/vector-icons";
import React, { useState } from "react";
import { Text, View, StyleSheet, TextInput, FlatList, TouchableOpacity, ActivityIndicator, Alert } from "react-native";
import * as DocumentPicker from 'expo-document-picker';
import EmailModal from "../modals/EmailModal";
import CalendarModal from "../modals/CalendarModal";

let messageCounter = 0;

export default function ChatScreen() {
  const [messages, setMessages] = useState<{ id: string; text: string; sender: string }[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isEmailModalVisible, setIsEmailModalVisible] = useState(false);
  const [isCalendarModalVisible, setIsCalendarModalVisible] = useState(false);
  const [emailDetails, setEmailDetails] = useState({
    recipient: '',
    subject: '',
    body: ''
  });
  const [calendarDetails, setCalendarDetails] = useState({
    title: '',
    location: '',
    startTime: '',
    endTime: '',
    description: '',
  });

  const [task, setTask] = useState('');

  const handleSend = async () => {
    if (input.trim()) {
      const uniqueId = `${Date.now()}-${messageCounter++}`;
      const newMessages = [...messages, { id: uniqueId, text: input, sender: "user" }];
      setMessages(newMessages);
      setInput('');
      setLoading(true);

      let apiMessage = "";
      const messageId = `${Date.now()}-${messageCounter++}`;

      setMessages((prevMessages) => [
        ...prevMessages,
        { id: messageId, text: "", sender: "bot" },
      ]);

      try {
        const response = await fetch("http://localhost:5000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            input: input,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to search the internet on the server");
        }
        const data = await response.json();

        console.log("Response from server:", data);
        if (data.task === "SEND_EMAIL") {
          setEmailDetails({
            recipient: data.response.email,
            subject: data.response.subject,
            body: data.response.body,
          });
          setIsEmailModalVisible(true); // Show the email modal
          apiMessage = "Please enter the email details";
          setMessages((prevMessages) =>
            prevMessages.map((msg) =>
              msg.id === messageId ? { ...msg, text: apiMessage } : msg
            )
          );
        } 
        else if (data.task === "SCHEDULE_MEETING") {
          setIsCalendarModalVisible(true); // Show the calendar modal
          apiMessage = "Please enter the meeting details";
          setMessages((prevMessages) =>
            prevMessages.map((msg) =>
              msg.id === messageId ? { ...msg, text: apiMessage } : msg
            )
          );
        } else {
          apiMessage = data.response;
          setMessages((prevMessages) =>
            prevMessages.map((msg) =>
              msg.id === messageId ? { ...msg, text: apiMessage } : msg
            )
          );
        }
      } catch (error) {
        console.error("Error searching the internet:", error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSendEmail = async (details: { recipient: string; subject: string; body: string }) => {
    console.log("Email details:", details);
    // setIsEmailModalVisible(false);
    const response = await fetch("http://localhost:5000/send_email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        to: details.recipient,
        subject: details.subject,
        body: details.body,
      })
    });

    let message = "";
    if (!response.ok) {
      message = "Failed to send email";
    } else {
      message = "Email sent successfully";
    }

    setMessages((prevMessages) => [
      ...prevMessages,
      { id: `${Date.now()}-${messageCounter++}`, text: message, sender: "bot" },
    ]);
  };

  const handleScheduleMeeting = async (details: { title: string; location: string; startTime: string; endTime: string; description: string }) => {
    console.log("Meeting details:", details);

    try {
      const response = await fetch("http://localhost:5000/schedule_meeting", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          summary: details.title,
          location: details.location,
          start_time: details.startTime,
          end_time: details.endTime,
          description: details.description,
        }),
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        throw new Error(errorResponse.error || "Failed to schedule meeting");
      }

      const responseData = await response.json();
      const successMessage = `Meeting scheduled successfully! View it here: ${responseData.event_link}`;

      setMessages((prevMessages) => [
        ...prevMessages,
        { id: `${Date.now()}-${messageCounter++}`, text: successMessage, sender: "bot" },
      ]);

      setIsCalendarModalVisible(false);
    } catch (error) {
      console.error("Error scheduling meeting:", error);
      const errorMessage = typeof error === "string" ? error : (error as Error).message;

      setMessages((prevMessages) => [
        ...prevMessages,
        { id: `${Date.now()}-${messageCounter++}`, text: `Error: ${errorMessage}`, sender: "bot" },
      ]);
    }
  };


  const handleAddPDF = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: 'application/pdf',
      multiple: true
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      setLoading(true);
      try {
        for (const selectedFile of result.assets) {
          const response = await fetch(selectedFile.uri);
          const blob = await response.blob();
          const reader = new FileReader();

          // Show uploading message in chat
          const uniqueId = `${Date.now()}-${messageCounter++}`;
          let dotCounter = 0;
          const initialText = `Uploading ${selectedFile.name}`;
          setMessages((prevMessages) => [
            ...prevMessages,
            { id: uniqueId, text: initialText, sender: "bot" },
          ]);

          // Create interval for animated dots
          const intervalId = setInterval(() => {
            dotCounter = (dotCounter + 1) % 4;
            const animatedText = initialText + ".".repeat(dotCounter);
            setMessages((prevMessages) =>
              prevMessages.map((msg) =>
                msg.id === uniqueId ? { ...msg, text: animatedText } : msg
              )
            );
          }, 500);

          reader.onloadend = async () => {
            clearInterval(intervalId); // Stop the animation
            if (reader.result === null) {
              Alert.alert('Error', 'Failed to read file');
              return;
            }
            const base64Data = (reader.result as string).split(',')[1]; // Remove data URI prefix

            const serverResponse = await fetch('http://localhost:5000/upload_pdf', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                file: base64Data,
                fileName: selectedFile.name
              }),
            });

            const data = await serverResponse.json();
            console.log("PDF Upload Success:", data);
            setTask("READ_PDF");

            // Update message to "Uploaded" after successful upload
            setMessages((prevMessages) =>
              prevMessages.map((msg) =>
                msg.id === uniqueId ? { ...msg, text: `Uploaded ${selectedFile.name} successfully` } : msg
              )
            );
          };

          reader.readAsDataURL(blob); // Converts file to base64
        }
        setLoading(false);
      } catch (error) {
        console.error("Error uploading PDF:", error);
      } finally {
        setLoading(false);
      }
    }
  };

  const clearMessages = async () => {
    try {
      // Call the backend API to clear documents
      const response = await fetch("http://localhost:5000/clear_history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to clear documents on the server");
      }

      const data = await response.json();
      console.log(data.message); // Log the response message if needed

      // Clear messages in the chat
      setMessages([]);
    } catch (error) {
      console.error("Error clearing messages:", error);
    }
  };


  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.spacer} />
        <View style={styles.headerTextContainer}>
          <Text style={styles.headerText}>Personal Chat</Text>
        </View>
        <View style={styles.clearButtonContainer}>
          <TouchableOpacity onPress={clearMessages} style={styles.clearButton}>
            <Ionicons name="trash" size={18} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>
      <FlatList
        data={messages}
        renderItem={({ item }) => (
          <View
            style={[
              styles.messageBubble,
              item.sender === "user" ? styles.userBubble : styles.botBubble,
            ]}
          >
            <Text style={styles.messageText}>{item.text}</Text>
          </View>
        )}
        keyExtractor={(item) => item.id}
        style={styles.messageList}
      />

      <View style={styles.inputContainer}>
        <TouchableOpacity style={styles.addButton} onPress={handleAddPDF}>
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          placeholder="Type a message..."
          placeholderTextColor="#888"
          value={input}
          onChangeText={setInput}
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSend} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>


      <EmailModal
        visible={isEmailModalVisible}
        onClose={() => setIsEmailModalVisible(false)}
        onSend={handleSendEmail}
        emailDetails={emailDetails}
      />


      <CalendarModal
        visible={isCalendarModalVisible}
        onClose={() => setIsCalendarModalVisible(false)}
        onSchedule={handleScheduleMeeting}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#25292e',
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    padding: 10,
    justifyContent: "space-between",
  },
  headerTextContainer: {
    flex: 2,
    alignItems: "center",
  },
  headerText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
    flex: 1,
    alignItems: "center",
  },
  spacer: {
    flex: 1,
  },
  clearButtonContainer: {
    flex: 1,
    alignItems: "flex-end",
  },
  clearButton: {
    backgroundColor: "transparent",
    borderRadius: 5,
    padding: 8,
  },
  clearButtonText: {
    color: "#fff",
    fontWeight: "bold",
  },
  messageList: {
    flex: 1,
    padding: 10,
  },
  messageBubble: {
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
    maxWidth: '80%',
  },
  userBubble: {
    backgroundColor: '#3e4551',
    alignSelf: 'flex-end',
  },
  botBubble: {
    backgroundColor: '#1c75bc',
    alignSelf: 'flex-start',
  },
  messageText: {
    color: '#fff',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    backgroundColor: '#3e4551',
    color: '#fff',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginRight: 10,
  },
  sendButton: {
    backgroundColor: '#1c75bc',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  addButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 10,
    backgroundColor: 'transparent',
    borderRadius: 20,
    margin: 10,
  },
  addButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    marginLeft: 5,
  },
});
