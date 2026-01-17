import express from "express";
import { protect } from "../middleware/authmiddleware.js";
import { createproject, getProjectById   } from "../controllers/project_controllers.js";

const router = express.Router();

router.post("/" ,protect, createproject);
router.get("/:id", protect, getProjectById);

export default router;