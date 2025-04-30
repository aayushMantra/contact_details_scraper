import axios from "axios";

// Change this line to use process.env instead of import.meta.env
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8007";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};

export const getProcessingStatus = async (jobId) => {
  try {
    const response = await api.get(`/status/${jobId}`);
    return response.data;
  } catch (error) {
    console.error("Error checking status:", error);
    throw error;
  }
};

export const downloadProcessedFile = async (jobId) => {
  try {
    const response = await api.get(`/download/${jobId}`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `processed_contacts_${jobId}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    return true;
  } catch (error) {
    console.error("Error downloading file:", error);
    throw error;
  }
};
