const server = require('./server.js');
const supertest = require('supertest');
const requestWithSupertest = supertest(server);
const { DateTime } = require('luxon');

describe('/messages', () => {
  test('list of messages', async () => {
    const res = await requestWithSupertest.get('/api/messages');
    expect(res.status).toEqual(200);
    expect(res.type).toEqual(expect.stringContaining('json'));
    expect(res.body.length).toBeGreaterThan(0);
    expect(res.body[0]).toHaveProperty('id');
    expect(res.body[0]).toHaveProperty('created_at');
  });

  test('sort by play count', async () => {
    const res = await requestWithSupertest.get(
      '/api/messages?sort=play_count&direction=asc'
    );
    for (const index in res.body) {
      if (index === '0') {
        continue;
      }
      expect(res.body[index].play_count).toBeGreaterThanOrEqual(
        res.body[index - 1].play_count
      );
    }
  });
});

describe('GET /message/:id', () => {
  test('details of message', async () => {
    const res = await requestWithSupertest.get('/api/message/1');
    expect(res.status).toEqual(200);
    expect(res.type).toEqual(expect.stringContaining('json'));
    expect(res.body).toHaveProperty('message');
    expect(res.body.message.id).toEqual(1);
  });

  test('previous and next message', async () => {
    const res = await requestWithSupertest.get('/api/message/3');
    expect(res.status).toEqual(200);
    expect(res.type).toEqual(expect.stringContaining('json'));
    expect(res.body).toHaveProperty('message');
    expect(res.body).toHaveProperty('previous');
    expect(res.body).toHaveProperty('next');
    expect(
      DateTime.fromSQL(res.body.previous.created_at).toMillis()
    ).toBeLessThan(DateTime.fromSQL(res.body.message.created_at).toMillis());
  });

  test('404 on non-existent ID', async () => {
    const res = await requestWithSupertest.get('/api/message/0');
    expect(res.status).toEqual(404);
  });
});

describe('DELETE /message/:id', () => {
  test('deletes message', async () => {
    expect((await requestWithSupertest.delete('/api/message/1')).status).toEqual(204);
  });
});