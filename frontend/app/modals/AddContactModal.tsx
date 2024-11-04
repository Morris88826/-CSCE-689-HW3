import React, { useState, useEffect } from 'react';
import { Modal, View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

interface Contact {
    name: string;
    email: string;
    phone?: string; // Optional field
}

interface AddContactModalProps {
    visible: boolean;
    onClose: () => void;
    onAddOrEdit: (contact: Contact) => void;
    initialContact?: Contact;
    mode: 'add' | 'edit';
}

const AddContactModal: React.FC<AddContactModalProps> = ({ visible, onClose, onAddOrEdit, initialContact, mode }) => {
    const [contact, setContact] = useState<Contact>({ name: '', email: '', phone: '' });
    const [errors, setErrors] = useState({ name: '', email: '' });

    useEffect(() => {
        if (mode === 'edit' && initialContact) {
            setContact(initialContact);
        } else if (mode === 'add') {
            setContact({ name: '', email: '', phone: '' });
        }
        setErrors({ name: '', email: '' }); // Reset errors when modal is opened
    }, [initialContact, mode, visible]);

    const validateAndSubmitContact = () => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        let hasError = false;
        const newErrors = { name: '', email: '' };

        if (contact.name.trim() === '') {
            newErrors.name = 'Name is required.';
            hasError = true;
        }
        if (!emailRegex.test(contact.email)) {
            newErrors.email = 'Please enter a valid email address.';
            hasError = true;
        }

        setErrors(newErrors);
        if (!hasError) {
            onAddOrEdit(contact);
            if (mode === 'add') {
                setContact({ name: '', email: '', phone: '' }); // Clear form for add mode
            }
            onClose(); // Close the modal after submitting
        }
    };

    return (
        <Modal visible={visible} animationType="slide" transparent={true} onRequestClose={onClose}>
            <View style={styles.modalContainer}>
                <View style={styles.modalContent}>
                    <Text style={styles.modalTitle}>{mode === 'add' ? 'Add New Contact' : 'Edit Contact'}</Text>

                    <TextInput
                        style={[styles.input, errors.name ? styles.inputError : null]}
                        placeholder="Name"
                        value={contact.name}
                        onChangeText={(text) => setContact({ ...contact, name: text })}
                    />
                    {errors.name ? <Text style={styles.errorText}>{errors.name}</Text> : null}

                    <TextInput
                        style={[styles.input, errors.email ? styles.inputError : null]}
                        placeholder="Email"
                        value={contact.email}
                        onChangeText={(text) => setContact({ ...contact, email: text })}
                    />
                    {errors.email ? <Text style={styles.errorText}>{errors.email}</Text> : null}

                    <TextInput
                        style={styles.input}
                        placeholder="Phone (optional)"
                        value={contact.phone}
                        onChangeText={(text) => setContact({ ...contact, phone: text })}
                    />

                    <View style={styles.buttonContainer}>
                        <TouchableOpacity onPress={validateAndSubmitContact} style={styles.sendButton}>
                            <Text style={styles.buttonText}>{mode === 'add' ? 'Add' : 'Save'}</Text>
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

export default AddContactModal;

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
    inputError: {
        borderColor: '#d9534f',
        borderWidth: 1,
        backgroundColor: '#ffe6e6',
    },
    errorText: {
        color: '#d9534f',
        alignSelf: 'flex-start',
        marginBottom: 8,
        fontSize: 12,
    },
    buttonContainer: {
        flexDirection: 'row',
        marginTop: 20,
    },
    sendButton: {
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
