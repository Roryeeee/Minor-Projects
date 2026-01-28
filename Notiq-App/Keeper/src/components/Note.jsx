import React, { useState } from "react";
import RemoveIcon from "@mui/icons-material/Remove";
import EditIcon from "@mui/icons-material/Edit";
import { Fab, Zoom } from "@mui/material";

function Note(props) {
  //State for Editing the note
  const [isEditing, setIsEditing] = useState(false);
  const [editedNote, setEditedNote] = useState({
    title: props.title,
    content: props.content
  });
  //States for the Conditional rendering of the buttons
  const [isMouseOver, setMouseOver] = useState(false);
  const [isMouseO, setMouseO] = useState(false);
  const [isMousO, setMousO] = useState(false);

  function handleDelete() {
    props.onDelete(props.id);
  }

  function handleEdit() {
    setIsEditing(true);
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setEditedNote(prev => ({
      ...prev,
      [name]: value
    }));
  }

  function handleSave() {
    props.onEdit(props.id, editedNote); // Assuming you’ll add `onEdit` in `App.jsx`
    setIsEditing(false);
  }

  function handleMouseOver() {
    setMouseOver(true);
  }

  function handleMouseOut() {
    setMouseOver(false);
  }

  function handleMouseO() {
    setMouseO(true);
  }

  function handleMouseOu() {
    setMouseO(false);
  }

  function handleMousO() {
    setMousO(true);
  }

  function handleMousOu() {
    setMousO(false);
  }

  return (
    <div className="note">
      {isEditing ? (
        <>
          <div className="edit-input">
          <input
            type="text"
            name="title"
            value={editedNote.title}
            onChange={handleChange}
            
          />
          </div>
          <div className="edit-textarea"><textarea
            name="content"
            value={editedNote.content}
            onChange={handleChange}
          /></div>
          
          <div className="checkbtn"><Zoom in={true}>
            <Fab onClick={handleSave} size="small" style={{backgroundColor: isMousO ? "#ffffffe6":"#4caf50"  }}
            onMouseOver={handleMousO}
            onMouseOut={handleMousOu}>
              ✓
            </Fab>
          </Zoom></div>
        </>
      ) : (
        <>
          <h1>{props.title}</h1>
          <p>{props.content}</p>
          <div style={{ display: "flex", gap: "8px" }}>
            <Zoom in={true}>
              <Fab  
              onClick={handleEdit} 
              size="small" 
              style={{ backgroundColor: isMouseOver ? "#ffffffe6":"#f5ba13"  }}
              onMouseOver={handleMouseOver}
              onMouseOut={handleMouseOut}
              >
                <EditIcon />
              </Fab>
            </Zoom>
            <Zoom in={true}>
              <Fab onClick={handleDelete} size="small" style={{ backgroundColor: isMouseO ? "#ffffffe6":"#f5ba13"   }}
              onMouseOver={handleMouseO}
              onMouseOut={handleMouseOu}>
                <RemoveIcon />
              </Fab>
            </Zoom>
          </div>
        </>
      )}
    </div>
  );
}

export default Note;
