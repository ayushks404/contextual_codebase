import Query from "../models/query.js";
import axios from "axios";

export const ask_ques = async (req, res) => {
  try {
    const { project_id, question } = req.body;

    if (!project_id || !question) {
      return res.status(400).json({
        message: "Project ID and question are required",
      });
    }
    const AI_SERVICE = process.env.AI_SERVICE_URL;

    const airesponse = await axios.post(`${AI_SERVICE}/query`, {
      project_id,
      question,
    });

    
    const result = {
      answer: airesponse.data.answer || airesponse.data.ans || airesponse.data.response,
      sources: airesponse.data.sources || [],
    };

    
    await Query.create({
      projectId: project_id,
      userId: req.user._id,
      question,
      answer: result.answer,
      sources: result.sources,
    });

    
    return res.json(result);

  } catch (err) {
    console.error("query err", err);
    return res.status(500).json({
      message: "Cannot process query",
    });
  }
};
