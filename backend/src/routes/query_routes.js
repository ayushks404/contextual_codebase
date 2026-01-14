import express from "express";
import { protect } from "../middleware/authmiddleware.js";
import { ask_ques } from "../controllers/querry_controllers.js";

const router = express.Router();

router.post("/" ,protect, ask_ques);

export default router;