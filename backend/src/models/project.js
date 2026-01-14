import mongoose from "mongoose";

const projectschema = new mongoose.Schema({
        name : {
            type:String,
            required: true,
        },
        repoUrl: {
            type: String,
            required: true,
            unique: true
        },
        owner : {
            type:mongoose.Schema.Types.ObjectId,
            ref :"User",
        },
        index :{
            type:Boolean,
            default:false
        },
        
    },{ timestamps:true }
);

export default mongoose.model("Project",projectschema);