const express = require("express");
const app = express();
const fs = require("fs");

const port = 3000;

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.get("/api/log", (req, res) => {
  const log = fs.readFileSync("../telephone.log").toString().trim();
  res.send(
    log.split("\n").map((line) => {
      const [date, level, module, message] = line.split("|");
      return {
        date,
        level,
        module,
        message,
      };
    })
  );
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
