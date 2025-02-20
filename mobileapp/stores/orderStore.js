import { create } from 'zustand';

export const useOrderStore = create((set) => ({
  orders: [],
  addOrder: (order) => set((state) => ({ 
    orders: [...state.orders, order] 
  })),
  removeOrder: (xcus) => set((state) => ({ 
    orders: state.orders.filter(order => order.xcus !== xcus) 
  })),
  clearOrders: () => set({ orders: [] }),
}));