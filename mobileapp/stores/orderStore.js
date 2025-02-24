import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useOrderStore = create((set) => ({
  orders: [],
  loadOrders: async () => {
    try {
      const storedOrders = await AsyncStorage.getItem("orders");
      if (storedOrders) {
        const { orders } = JSON.parse(storedOrders);
        set({ orders });
      }
    } catch (error) {
      console.error("Error loading orders:", error);
    }
  },
  addOrder: (order) => set((state) => ({ 
    orders: [...state.orders, order] 
  })),
  removeOrder: (xcus) => set((state) => ({ 
    orders: state.orders.filter(order => order.xcus !== xcus) 
  })),
  clearOrders: () => set({ orders: [] }),
}));