import express from "express";
import { protect } from "../middleware/authmiddleware.js";
import { createproject  } from "../controllers/project_controllers.js";

const router = express.Router();

router.post("/" ,protect, createproject);
export default router;