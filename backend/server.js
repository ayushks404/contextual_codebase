import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";

import auth_routes from "../backend/src/routes/auth_routes.js";
import project_routes from "../backend/src/routes/project_routes.js";
import query_routes from "../backend/src/routes/query_routes.js";


dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());


const connectdb = async () => {
    try{
        await mongoose.connect(process.env.MONGO_URI);
        console.log("mongodb connected");
    }
    catch (err){
        console.log("db error" , err.message);
        process.exit(1);
    }
};



app.get("/" , (req,res) => {
    res.send("backend running");
});


const PORT = process.env.PORT;
app.listen(PORT , () =>{
    console.log("server running on port 5000");
});

connectdb();




app.use("/api/query" , query_routes);
app.use("/api/auth" , auth_routes);
app.use("/api/project" , project_routes);

