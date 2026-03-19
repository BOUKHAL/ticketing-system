import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/",
});

api.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refresh = localStorage.getItem("refresh");

      if (refresh) {
        try {
          const res = await axios.post("http://localhost:8000/api/auth/token/refresh/", {
            refresh,
          });

          localStorage.setItem("access", res.data.access);
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          localStorage.removeItem("user");
          window.location.href = "/login";
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;