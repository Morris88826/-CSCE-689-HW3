import React, { useState, useEffect } from "react";
import { Modal, View, Text, TextInput, TouchableOpacity, StyleSheet } from "react-native";

interface EmailDetails {
    recipient: string;
    subject: string;
    body: string;
}

interface EmailModalProps {
    visible: boolean;
    onClose: () => void;
    onSend: (emailDetails: EmailDetails) => void;
    emailDetails: EmailDetails; // Added this
}

const EmailModal: React.FC<EmailModalProps> = ({ visible, onClose, onSend, emailDetails: initialEmailDetails }) => {
    const [emailDetails, setEmailDetails] = useState<EmailDetails>({
        recipient: '',
        subject: '',
        body: ''
    });

    const [errors, setErrors] = useState({
        recipient: '',
        subject: '',
        body: ''
    });

    // Sync the modal's state with the initialEmailDetails prop when it becomes visible
    useEffect(() => {
        if (visible) {
            setEmailDetails({
                recipient: initialEmailDetails.recipient || '',
                subject: initialEmailDetails.subject || '',
                body: initialEmailDetails.body || '',
            });
        }
    }, [visible, initialEmailDetails]);

    // Validation function to check if email format is valid and fields are non-empty
    const validateAndSendEmail = () => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        let hasError = false;
        const newErrors = { recipient: '', subject: '', body: '' };

        if (!emailRegex.test(emailDetails.recipient)) {
            newErrors.recipient = 'Please enter a valid email address.';
            hasError = true;
        }

        if (emailDetails.subject.trim() === '') {
            newErrors.subject = 'Subject is required.';
            hasError = true;
        }

        setErrors(newErrors);
        if (!hasError) {
            onSend(emailDetails);
            setEmailDetails({ recipient: '', subject: '', body: '' }); // Reset form after sending
            onClose(); // Close the modal after sending
        }
    };

    return (
        <Modal
            visible={visible}
            animationType="slide"
            transparent={true}
            onRequestClose={onClose}
        >
            <View style={styles.modalContainer}>
                <View style={styles.modalContent}>
                    <Text style={styles.modalTitle}>Compose Email</Text>

                    <TextInput
                        style={[styles.input, errors.recipient ? styles.inputError : null]}
                        placeholder="Recipient"
                        value={emailDetails.recipient || ''}
                        onChangeText={(text) => setEmailDetails({ ...emailDetails, recipient: text })}
                    />
                    {errors.recipient ? <Text style={styles.errorText}>{errors.recipient}</Text> : null}

                    <TextInput
                        style={[styles.input, errors.subject ? styles.inputError : null]}
                        placeholder="Subject"
                        value={emailDetails.subject || ''}
                        onChangeText={(text) => setEmailDetails({ ...emailDetails, subject: text })}
                    />
                    {errors.subject ? <Text style={styles.errorText}>{errors.subject}</Text> : null}

                    <TextInput
                        style={[styles.input, styles.textArea]}
                        placeholder="Body"
                        value={emailDetails.body || ''}
                        onChangeText={(text) => setEmailDetails({ ...emailDetails, body: text })}
                        multiline
                    />
                    <View style={styles.buttonContainer}>
                        <TouchableOpacity onPress={validateAndSendEmail} style={styles.sendButton}>
                            <Text style={styles.buttonText}>Send</Text>
                        </TouchableOpacity>
                        <TouchableOpacity onPress={onClose} style={styles.cancelButton}>
                            <Text style={styles.buttonText}>Cancel</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </View>
        </Modal>
    );
};

export default EmailModal;

const styles = StyleSheet.create({
    modalContainer: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "rgba(0, 0, 0, 0.5)"
    },
    modalContent: {
        width: "85%",
        padding: 20,
        backgroundColor: "#fff",
        borderRadius: 10,
        alignItems: "center"
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: "bold",
        marginBottom: 15
    },
    input: {
        width: "100%",
        backgroundColor: "#f1f1f1",
        padding: 10,
        borderRadius: 5,
        marginVertical: 8
    },
    inputError: {
        borderColor: "#d9534f",
        borderWidth: 1,
        backgroundColor: "#ffe6e6"
    },
    textArea: {
        height: 100,
        textAlignVertical: "top"
    },
    errorText: {
        color: "#d9534f",
        alignSelf: "flex-start",
        marginBottom: 8,
        fontSize: 12
    },
    buttonContainer: {
        flexDirection: "row",
        marginTop: 20
    },
    sendButton: {
        backgroundColor: "#1c75bc",
        padding: 10,
        borderRadius: 5,
        marginHorizontal: 5,
        alignItems: "center",
        width: "40%"
    },
    cancelButton: {
        backgroundColor: "#d9534f",
        padding: 10,
        borderRadius: 5,
        marginHorizontal: 5,
        alignItems: "center",
        width: "40%"
    },
    buttonText: {
        color: "#fff",
        fontWeight: "bold"
    }
});
