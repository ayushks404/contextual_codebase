
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
    axios.post("http://localhost:8000/index-repo", {
      project_id: project._id,
      repo_url: repourl,
    }).catch(err => {
      console.log("AI indexing failed:", err.message);
    });



    res.status(201).json({ project });

  } catch (err) {
    console.error("Create project error:", err);
    res.status(500).json({ message: err.message });
  }
};

