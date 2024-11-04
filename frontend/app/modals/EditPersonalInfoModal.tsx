import React, { useState, useEffect } from 'react';
import { Modal, View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

interface PersonalInfo {
  firstName: string;
  lastName: string;
  phone: string;
  birthday: string;
  email: string;
}

interface EditPersonalInfoModalProps {
  visible: boolean;
  onClose: () => void;
  onSave: (info: PersonalInfo) => void;
  initialInfo: PersonalInfo;
}

const EditPersonalInfoModal: React.FC<EditPersonalInfoModalProps> = ({ visible, onClose, onSave, initialInfo }) => {
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>(initialInfo);

  useEffect(() => {
    if (visible) {
      setPersonalInfo(initialInfo);
    }
  }, [visible, initialInfo]);

  const handleSave = () => {
    onSave(personalInfo);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent={true} onRequestClose={onClose}>
      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Edit Personal Information</Text>

          <TextInput
            style={styles.input}
            placeholder="First Name"
            value={personalInfo.firstName}
            onChangeText={(text) => setPersonalInfo({ ...personalInfo, firstName: text })}
          />
          <TextInput
            style={styles.input}
            placeholder="Last Name"
            value={personalInfo.lastName}
            onChangeText={(text) => setPersonalInfo({ ...personalInfo, lastName: text })}
          />
          <TextInput
            style={styles.input}
            placeholder="Phone"
            value={personalInfo.phone}
            onChangeText={(text) => setPersonalInfo({ ...personalInfo, phone: text })}
          />
          <TextInput
            style={styles.input}
            placeholder="Birthday (YYYY-MM-DD)"
            value={personalInfo.birthday}
            onChangeText={(text) => setPersonalInfo({ ...personalInfo, birthday: text })}
          />
          <TextInput
            style={styles.input}
            placeholder="Email"
            value={personalInfo.email}
            onChangeText={(text) => setPersonalInfo({ ...personalInfo, email: text })}
          />

          <View style={styles.buttonContainer}>
            <TouchableOpacity onPress={handleSave} style={styles.saveButton}>
              <Text style={styles.buttonText}>Save</Text>
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

export default EditPersonalInfoModal;

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    width: '85%',
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  input: {
    width: '100%',
    backgroundColor: '#f1f1f1',
    padding: 10,
    borderRadius: 5,
    marginVertical: 8,
  },
  buttonContainer: {
    flexDirection: 'row',
    marginTop: 20,
  },
  saveButton: {
    backgroundColor: '#1c75bc',
    padding: 10,
    borderRadius: 5,
    marginHorizontal: 5,
    alignItems: 'center',
    width: '40%',
  },
  cancelButton: {
    backgroundColor: '#d9534f',
    padding: 10,
    borderRadius: 5,
    marginHorizontal: 5,
    alignItems: 'center',
    width: '40%',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});
