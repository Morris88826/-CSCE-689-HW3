import React, { useState, useEffect } from 'react';
import { Text, View, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import AddContactModal from '../modals/AddContactModal';
import EditPersonalInfoModal from '../modals/EditPersonalInfoModal';

interface PersonalInfo {
  firstName: string;
  lastName: string;
  phone: string;
  birthday: string;
  email: string;
}

interface Contact {
  id: number;  // Make sure ID is required for database consistency
  name: string;
  email: string;
  phone: string;
}

export default function Index() {
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>({
    firstName: '',
    lastName: '',
    phone: '',
    birthday: '',
    email: '',
  });
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isAddContactModalVisible, setAddContactModalVisible] = useState(false);
  const [isEditInfoModalVisible, setEditInfoModalVisible] = useState(false);
  const [editContactId, setEditContactId] = useState<number | null>(null);

  // Fetch personal information and contacts on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const personalInfoResponse = await fetch('http://localhost:5000/get_personal_info');
        const personalInfoData = await personalInfoResponse.json();
        if (personalInfoData.personalInfo) setPersonalInfo(personalInfoData.personalInfo);

        const contactsResponse = await fetch('http://localhost:5000/get_contacts');
        const contactsData = await contactsResponse.json();
        if (contactsData.contacts) setContacts(contactsData.contacts);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const handleAddContact = async (contact: Contact) => {
    try {
      if (editContactId !== null) {
        // Edit existing contact
        const contactToUpdate = contacts.find(c => c.id === editContactId);
        if (contactToUpdate) {
          const response = await fetch(`http://localhost:5000/update_contact/${editContactId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contact),
          });
          if (response.ok) {
            setContacts(prevContacts =>
              prevContacts.map(c => (c.id === editContactId ? { ...contact, id: editContactId } : c))
            );
            setEditContactId(null);
          } else {
            Alert.alert('Error', 'Failed to update contact');
          }
        }
      } else {
        // Add new contact
        const response = await fetch('http://localhost:5000/add_contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(contact),
        });
        if (response.ok) {
          const newContact = await response.json(); // Get the contact returned from the server
          if (newContact.id) {
            setContacts(prevContacts => [...prevContacts, newContact]); // Add new contact to state
          } else {
            Alert.alert('Error', 'Failed to add contact');
          }
        } else {
          Alert.alert('Error', 'Failed to add contact');
        }
      }
    } catch (error) {
      console.error('Error adding/updating contact:', error);
    }
    setAddContactModalVisible(false);
  };

  const handleEditContact = (contactId: number) => {
    setEditContactId(contactId);
    setAddContactModalVisible(true);
  };

  const handleDeleteContact = async (contactId: number) => {
    if (contactId !== undefined) {
      try {
        const response = await fetch(`http://localhost:5000/delete_contact/${contactId}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          setContacts(prevContacts => prevContacts.filter(contact => contact.id !== contactId));
          Alert.alert('Success', 'Contact deleted successfully');
        } else {
          Alert.alert('Error', 'Failed to delete contact');
        }
      } catch (error) {
        console.error('Error deleting contact:', error);
      }
    } else {
      console.error('Invalid contact ID:', contactId);
    }
  };

  const handleEditInfoSave = async (updatedInfo: PersonalInfo) => {
    try {
      const response = await fetch('http://localhost:5000/update_personal_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedInfo),
      });
      if (response.ok) {
        setPersonalInfo(updatedInfo);
      } else {
        Alert.alert('Error', 'Failed to update personal information');
      }
    } catch (error) {
      console.error('Error updating personal info:', error);
    }
    setEditInfoModalVisible(false);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTextContainer}>
          <Text style={styles.headerText}>Home</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardHeader}>Personal Information</Text>
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>First Name: {personalInfo.firstName}</Text>
          <Text style={styles.infoText}>Last Name: {personalInfo.lastName}</Text>
          <Text style={styles.infoText}>Email: {personalInfo.email}</Text>
          <Text style={styles.infoText}>Phone: {personalInfo.phone}</Text>
          <Text style={styles.infoText}>Birthday: {personalInfo.birthday}</Text>
        </View>
        <TouchableOpacity onPress={() => setEditInfoModalVisible(true)} style={styles.button}>
          <Text style={styles.buttonText}>Edit Personal Information</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardHeader}>Contacts</Text>
        <ScrollView style={styles.contactList}>
          {contacts.map((contact) => (
            <View key={contact.id} style={styles.contactContainer}>
              <View style={styles.contactInfo}>
                <Text style={styles.infoText}>{contact.name}</Text>
                <Text style={styles.infoText}>{contact.email}</Text>
                <Text style={styles.infoText}>{contact.phone}</Text>
              </View>
              <View style={styles.contactActions}>
                <TouchableOpacity style={styles.editButton} onPress={() => handleEditContact(contact.id)}>
                  <Text style={styles.buttonText}>Edit</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.deleteButton} onPress={() => handleDeleteContact(contact.id)}>
                  <Text style={styles.buttonText}>Delete</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </ScrollView>
        <TouchableOpacity onPress={() => { setAddContactModalVisible(true); setEditContactId(null); }} style={styles.button}>
          <Text style={styles.buttonText}>Add New Contact</Text>
        </TouchableOpacity>
      </View>

      {/* AddContactModal */}
      <AddContactModal
        visible={isAddContactModalVisible}
        onClose={() => setAddContactModalVisible(false)}
        onAddOrEdit={handleAddContact}
        initialContact={editContactId !== null ? contacts.find(contact => contact.id === editContactId) : undefined}
        mode={editContactId !== null ? 'edit' : 'add'}
      />

      {/* EditPersonalInfoModal */}
      <EditPersonalInfoModal
        visible={isEditInfoModalVisible}
        onClose={() => setEditInfoModalVisible(false)}
        onSave={handleEditInfoSave}
        initialInfo={personalInfo}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#25292e',
    padding: 20,
  },
  header: {
    fontSize: 24,
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
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
  card: {
    backgroundColor: '#3b3b3b',
    borderRadius: 10,
    padding: 15,
    marginBottom: 20,
    width: '100%',
  },
  cardHeader: {
    fontSize: 20,
    color: '#fff',
    marginBottom: 10,
  },
  infoContainer: {
    marginBottom: 15,
  },
  infoText: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 5,
  },
  button: {
    backgroundColor: '#1c75bc',
    padding: 10,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  contactList: {
    maxHeight: 200,
  },
  contactContainer: {
    backgroundColor: '#4a4a4a',
    borderRadius: 5,
    padding: 10,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  contactInfo: {
    flex: 3,
  },
  contactActions: {
    flexDirection: 'row',
    gap: 10,
  },
  editButton: {
    backgroundColor: '#1c75bc',
    padding: 5,
    borderRadius: 3,
  },
  deleteButton: {
    backgroundColor: '#d9534f',
    padding: 5,
    borderRadius: 3,
  },
});
