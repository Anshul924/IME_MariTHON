// Import packages
const express = require("express");
const multer = require("multer");
const cors = require("cors");
const bodyParser = require("body-parser");
const path = require("path");

// Create express app
const app = express();
app.use(cors()); // allow frontend calls
app.use(bodyParser.json());

// File upload setup (files will be saved to /uploads folder)
const upload = multer({ dest: path.join(__dirname, "uploads/") });

// ================= ROUTES ==================

// File upload route
app.post("/upload", upload.fields([{ name: "sof" }, { name: "cp" }]), (req, res) => {
  console.log("Files uploaded:", req.files);

  res.json({
    success: true,
    message: "Files uploaded successfully!",
    files: req.files
  });
});

// Voyage details route
app.post("/voyage", (req, res) => {
  const details = req.body;
  console.log("Voyage details received:", details);

  // Example calculation (placeholder)
  const result = {
    totalTime: "72h 30m",
    events: [
      {
        event: "Arrived",
        start: "2025-08-01 08:00",
        end: "2025-08-01 10:00",
        duration: "2h",
        remarks: "Berthing"
      },
      {
        event: "Completed",
        start: "2025-08-03 12:00",
        end: "2025-08-04 08:30",
        duration: "20h 30m",
        remarks: "Cargo operations"
      }
    ]
  };

  res.json(result);
});

// ===========================================

// Start server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`✅ Backend running at http://localhost:${PORT}`);
});
