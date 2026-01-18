
import Project from "../models/project.js";
import axios from "axios";

export const createproject = async (req, res) => {
  try {

    const { name, repourl } = req.body;
    
    if (!name || !repourl) {
      return res.status(400).json({ message: "Name and repo URL required" });
    }

    //check duplicate
    const exists = await Project.findOne({ repourl });
    if (exists) {
      return res.status(400).json({ message: "Project already exists" });
    }

    //create a project in db
    const project = await Project.create({
      name,
      repourl,
      owner: req.user._id,
      indexed: false,
    });

    // call ai for indexing 
    const AI_SERVICE = process.env.AI_SERVICE_URL;

    axios.post(`${AI_SERVICE}/index-repo`, {
      project_id: project._id,
      repo_url: repourl,
    }).catch(err => {
      console.log("AI indexing failed:", err.message);
    });



    res.status(201).json({ project });

  }
  catch (err) {
    console.error("Create project error:", err);
    res.status(500).json({ message: err.message });
  }
};






export const getProjectById = async (req, res) => {
  
  try {
    const project = await Project.findOne({
      _id: req.params.id,
      owner: req.user._id,
    });

    if (!project) {
      return res.status(404).json({ message: "Project not found" });
    }

    res.json({
      name: project.name,
      repourl: project.repourl,
      indexed: project.index,
    });

  }
  catch (err) {
    console.error("Get project error:", err);
    res.status(500).json({ message: err.message });
  }
};
