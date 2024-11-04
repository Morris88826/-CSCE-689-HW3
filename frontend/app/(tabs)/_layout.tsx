import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007aff',
        headerShown: false,
      }}
    >
      <Tabs.Screen name="index" options={{ 
        title: 'Home',
        tabBarIcon: ({ color, focused }) => <Ionicons name={focused ? 'home-sharp' : 'home-outline'} color={color} size={24} />, 
      }} />
      <Tabs.Screen name="chat" options={{ 
        title: 'Chat' ,
        tabBarIcon: ({ color, focused }) => <Ionicons name={focused ? 'chatbubbles-sharp' : 'chatbubbles-outline'} color={color} size={24} />,
      }} />
    </Tabs>
  );
}
