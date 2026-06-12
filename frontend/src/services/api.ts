import axios from "axios";

export const api = axios.create({
  baseURL: "https://steven-summarizer.onrender.com"
});