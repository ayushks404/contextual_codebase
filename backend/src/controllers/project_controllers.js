import Project from "../models/project.js";
import axios  from "axios";

export const create_project = async (req , res) => {


    try{

        const {name , repourl } = req.body;

        if (!repourl || !name ) {
            return res.status(400).json({ message: "Please provide all fields" });
        }

        const urlExists = await user.findOne({ repourl });
        if (urlExists) {
            return res.status(400).json({ message: "project already exists" });
        }


        const project = await Project.create({
            name,
            repourl,
            owner: req.user.id,
            indexed: false
        });
        
        await axios.post("http://localhost:8000/index-repo", {
            projectId: project._id,
            repoUrl: project.repourl
        });



        res.status(201).json({
            project
        });

    } catch (err){
        res.status(500).json({
            message: err.message
        });
    }


};

