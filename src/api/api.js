import axios from "axios";
import { API_ENDPOINTS } from "./apiEndpoints.js";

export const API_URL = process.env.PUBLIC_URL;
// export const API_URL = "https://cdc6-194-226-199-9.ngrok-free.app/api";

const $api = axios.create({
  withCredentials: true,
  baseURL: API_URL,
});

// $api.interceptors.request.use((config) => {
//   config.headers.Authorization = `Bearer ${localStorage.getItem("token")}`;
//   config.headers["ngrok-skip-browser-warning"] = true;
//   return config;
// });

// $api.interceptors.response.use(
//   (config) => {
//     return config;
//   },
//   async (error) => {
//     const originalRequest = error.config;
//     if (
//       error.response?.status === 401 &&
//       error.config &&
//       !error.config._isRetry
//     ) {
//       originalRequest._isRetry = true;
//       try {
//         const response = await axios.get(
//           `${API_URL}/${API_ENDPOINTS.REFRESH_TOKEN}`,
//           { withCredentials: true }
//         );
//         localStorage.setItem("token", response.data.accessToken);
//         return $api.request(originalRequest);
//       } catch (e) {
//         console.log(e);
//         console.log("НЕ АВТОРИЗОВАН");
//       }
//     }
//     throw error;
//   }
// );

export default $api;

// const $api = {
//   get: async (url) => {
//     const response = await fetch(API_URL + url);
//     if (!response.ok) throw Error(response.statusText);
//     return await response.json();
//   },
//   post: async (url, data) => {
//     const response = await fetch(API_URL + url, {
//           method: "POST",
//           headers: {
//               "Content-Type": "application/json",
//           },
//           body: JSON.stringify(data),
//       });
//       return await response.json();
//   },
//   put: async (url, data) => {
//     const response = await fetch(API_URL + url, {
//           method: "PUT",
//           headers: {
//               "Content-Type": "application/json",
//           },
//           body: JSON.stringify(data),
//       });
//       return await response.json();
//   },
//   // Add other HTTP methods (PUT, DELETE, etc.) as needed
// };