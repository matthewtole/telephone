const express = require('express');
const app = express();
const fs = require('fs');
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const cors = require('cors');
const si = require('systeminformation');
const generateWaveform = require('generate-sound-waveform');
const path = require('path');
const morgan = require('morgan');

async function Db() {
  return await open({
    filename: '../telephone.db',
    driver: sqlite3.Database,
  });
}

app.use(cors());
app.use(morgan('short'))

app.get('/api/log', (req, res) => {
  const log = fs.readFileSync('../telephone.log').toString().trim();
  res.send(
    log.split('\n').map((line) => {
      const [date, level, module, message] = line.split('|');
      return {
        date,
        level,
        module,
        message,
      };
    })
  );
});

app.get('/api/system', async (req, res) => {
  res.send({
    time: si.time(),
    disks: await si.fsSize(),
    memory: await si.mem(),
  });
});

app.get('/api/messages', async (req, res) => {
  const sort = req.query.sort ?? 'created_at';
  const direction = req.query.direction ?? 'desc';

  const db = await Db();
  res.send(
    await db.all(`SELECT * FROM messages WHERE is_deleted=0 ORDER BY ${sort} ${direction}`)
  );
});

app.get('/api/message/:id', async (req, res) => {
  const db = await Db();
  const message = await db.get(
    `SELECT * FROM messages WHERE id=${Number(req.params.id)}`
  );
  if (message == null) {
    res.status(404).send();
    return;
  }
  const previous = await db.get(
    `SELECT * FROM messages WHERE created_at < ? AND is_deleted=0 ORDER BY created_at DESC`,
    [message.created_at]
  );
  const next = await db.get(
    `SELECT * FROM messages WHERE created_at > ? AND is_deleted=0 ORDER BY created_at ASC`,
    [message.created_at]
  );
  res.send({
    message,
    previous,
    next,
  });
});

app.get('/api/plays/:id', async (req, res) => {
  const db = await Db();
  const plays = await db.all(
    `SELECT * FROM plays WHERE message_id=${Number(
      req.params.id
    )} ORDER BY played_at DESC`
  );
  res.send({
    plays,
  });
});

app.get('/api/stats', async (req, res) => {
  const db = await Db();
  const messageCount = await db.get('SELECT COUNT(*) as count FROM messages WHERE is_deleted=0');
  const totalListens = await db.get('SELECT COUNT(*) as count FROM plays');
  const lastMessage = await db.get(
    'SELECT * FROM messages WHERE is_deleted=0 ORDER BY created_at DESC'
  );
  const lastPlay = await db.get('SELECT * FROM plays ORDER BY played_at DESC');
  res.send({
    messageCount: messageCount.count ?? 0,
    lastMessage,
    lastPlay,
    totalListens: totalListens.count ?? 0,
  });
});

app.get('/api/visualize', async (req, res, next) => {
  try {const stream = await generateWaveform.generateSoundImage(
    '../messages/' + req.query.filename,
    800,
    200,
    {
      stepMultiplier: 4,
      backgroundColor: '#fff',
      lineColor: '#277bc0',
      globalAplha: 1,
      lineWidth: 1,
    }
  );
  stream.pipe(res);
  } catch (ex) {
    console.error(ex);
    res.send('');
  }
});

app.delete('/api/message/:id', async (req, res) => {
  const db = await Db();
  await db.run(
    `UPDATE messages SET is_deleted=1 WHERE id=${Number(req.params.id)}`
  );
  res.status(204).send();
});

app.get('/api/logs/telephone', async (_, res) => {
  res.sendFile(path.resolve(__dirname + '/../telephone.log'));
});

app.get('/api/logs/website', async (_, res) => {
  res.sendFile(path.resolve(__dirname + '/../website.log'));
});

app.use(express.static('dist'));
app.use('/messages', express.static('../messages'));
app.get('/*', (req, res) => {
  res.sendFile(__dirname + '/dist/index.html');
});

module.exports = app;
