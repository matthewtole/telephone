const server = require('./server.js');
const supertest = require('supertest');
const requestWithSupertest = supertest(server);

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
