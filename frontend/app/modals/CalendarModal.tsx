import React, { useState } from 'react';
import { Modal, View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

interface CalendarDetails {
    title: string;
    location: string;
    description: string;
    startTime: Date;
    endTime: Date;
}

interface CalendarModalProps {
    visible: boolean;
    onClose: () => void;
    onSchedule: (calendarDetails: CalendarDetails) => void;
}

const CalendarModal: React.FC<CalendarModalProps> = ({ visible, onClose, onSchedule }) => {
    const [calendarDetails, setCalendarDetails] = useState<CalendarDetails>({
        title: '',
        location: '',
        description: '',
        startTime: new Date(),
        endTime: new Date(),
    });

    const [errors, setErrors] = useState({
        title: '',
    });

    const validateAndSchedule = () => {
        let hasError = false;
        const newErrors = { title: '' };

        if (calendarDetails.title.trim() === '') {
            newErrors.title = 'Title is required.';
            hasError = true;
        }

        setErrors(newErrors);
        if (!hasError) {
            onSchedule(calendarDetails);
            setCalendarDetails({
                title: '',
                location: '',
                description: '',
                startTime: new Date(),
                endTime: new Date(),
            });
            onClose();
        }
    };

    return (
        <Modal visible={visible} animationType="slide" transparent={true} onRequestClose={onClose}>
            <View style={styles.modalContainer}>
                <View style={styles.modalContent}>
                    <Text style={styles.modalTitle}>Schedule Event</Text>

                    <TextInput
                        style={[styles.input, errors.title ? styles.inputError : null]}
                        placeholder="Event Title *"
                        value={calendarDetails.title}
                        onChangeText={(text) => setCalendarDetails({ ...calendarDetails, title: text })}
                    />
                    {errors.title ? <Text style={styles.errorText}>{errors.title}</Text> : null}

                    <TextInput
                        style={styles.input}
                        placeholder="Location (optional)"
                        value={calendarDetails.location}
                        onChangeText={(text) => setCalendarDetails({ ...calendarDetails, location: text })}
                    />

                    <TextInput
                        style={[styles.input, styles.textArea]}
                        placeholder="Description"
                        value={calendarDetails.description}
                        onChangeText={(text) => setCalendarDetails({ ...calendarDetails, description: text })}
                        multiline
                    />

                    <Text style={styles.label}>Start Time:</Text>
                    <DatePicker
                        selected={calendarDetails.startTime}
                        onChange={(date: Date) => setCalendarDetails({ ...calendarDetails, startTime: date })}
                        showTimeSelect
                        dateFormat="yyyy-MM-dd HH:mm"
                        className="custom-datepicker"
                        popperPlacement="top-end"
                        popperClassName="custom-popper"
                        calendarClassName="custom-calendar"
                    />

                    <Text style={styles.label}>End Time:</Text>
                    <DatePicker
                        selected={calendarDetails.endTime}
                        onChange={(date: Date) => setCalendarDetails({ ...calendarDetails, endTime: date })}
                        showTimeSelect
                        dateFormat="yyyy-MM-dd HH:mm"
                        className="custom-datepicker"
                        popperPlacement="top-end"
                        popperClassName="custom-popper"
                        calendarClassName="custom-calendar"
                    />

                    <View style={styles.buttonContainer}>
                        <TouchableOpacity onPress={validateAndSchedule} style={styles.sendButton}>
                            <Text style={styles.buttonText}>Schedule</Text>
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

export default CalendarModal;

const styles = StyleSheet.create({
    modalContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.5)'
    },
    modalContent: {
        width: '85%',
        padding: 20,
        backgroundColor: '#fff',
        borderRadius: 10,
        alignItems: 'center'
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 15
    },
    input: {
        width: '100%',
        backgroundColor: '#f1f1f1',
        padding: 10,
        borderRadius: 5,
        marginVertical: 8
    },
    inputError: {
        borderColor: '#d9534f',
        borderWidth: 1,
        backgroundColor: '#ffe6e6'
    },
    textArea: {
        height: 80,
        textAlignVertical: 'top'
    },
    errorText: {
        color: '#d9534f',
        alignSelf: 'flex-start',
        marginBottom: 8,
        fontSize: 12
    },
    label: {
        alignSelf: 'flex-start',
        marginTop: 10,
        marginBottom: 5,
        fontSize: 14,
        fontWeight: 'bold'
    },
    buttonContainer: {
        flexDirection: 'row',
        marginTop: 20
    },
    sendButton: {
        backgroundColor: '#1c75bc',
        padding: 10,
        borderRadius: 5,
        marginHorizontal: 5,
        alignItems: 'center',
        width: '40%'
    },
    cancelButton: {
        backgroundColor: '#d9534f',
        padding: 10,
        borderRadius: 5,
        marginHorizontal: 5,
        alignItems: 'center',
        width: '40%'
    },
    buttonText: {
        color: '#fff',
        fontWeight: 'bold'
    }
});
