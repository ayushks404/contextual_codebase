import express from "express";
import { protect } from "../middleware/authmiddleware.js";
import { create_project } from "../controllers/project_controllers.js";

const router = express.Router();

router.post("/" ,protect, create_project);

export default router;