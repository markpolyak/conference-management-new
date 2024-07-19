import axios from "axios";
import { create } from "zustand";
import { API_URL } from "../api/api";
import { API_ENDPOINTS } from "../api/apiEndpoints";


const useAuthStore = create((set) => ({
  isAuth: true,
  user: {email: "Arthur1203@yandex.ru", password: "" },

  setAuth: (flag) => set(() => ({ isAuth: flag })),

  login: (email, password) => {
      set((state) => ({ user: { ...state.user, email: email, password: password }, isAuth: true})); 
  },
  logout: () => {
      set((state) => ({ user: { ...state.user, email: "", password: ""}, isAuth: false})); 
  },
}));

export default useAuthStore;