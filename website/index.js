const express = require("express");
const app = express();
const fs = require("fs");
const sqlite3 = require("sqlite3");
const { open } = require("sqlite");

const port = 3000;

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

app.get("/api/messages", async (req, res) => {
  const db = await open({
    filename: "../telephone.db",
    driver: sqlite3.Database,
  });
  res.send(await db.all("SELECT * FROM messages"));
});

app.use(express.static("public"));
app.use("/messages", express.static("../messages"));

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
