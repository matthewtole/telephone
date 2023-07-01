import React from 'react';
import { DateTime, Duration } from 'luxon';
import { useQuery } from 'react-query';
import { API_ROOT } from '../config';
import { formatDate } from './MessageList';
import { system, Systeminformation } from 'systeminformation';
import { Message, Play } from '../types';
import { Link } from 'react-router-dom';

export const Home: React.FC = () => {
  const statsQuery = useQuery<{
    messageCount: number;
    lastMessage?: Message;
    lastPlay?: Play;
    totalListens: number;
  }>('stats', () => fetch(`${API_ROOT}/stats`).then((res) => res.json()), {
    refetchInterval: 1000,
  });

  const systemQuery = useQuery<{
    time: Systeminformation.TimeData;
    disks: Systeminformation.FsSizeData[];
    memory: Systeminformation.MemData;
  }>('system', () => fetch(`${API_ROOT}/system`).then((res) => res.json()), {
    refetchInterval: 1000,
  });

  const largestDisk =
    systemQuery.data == null
      ? null
      : systemQuery.data.disks.reduce((largest, current) => {
          return largest.size > current.size ? largest : current;
        }, systemQuery.data.disks[0]);

  return (
    <main>
      <div className="stats">
        {statsQuery.data != null && (
          <>
            <Link className="info-block" to="/messages">
              <span className="value">{statsQuery.data.messageCount}</span>
              <span className="label">Total Messages</span>
            </Link>
            {statsQuery.data.lastMessage != null && (
              <Link
                className="info-block"
                to={`/messages/${statsQuery.data.lastMessage.id}`}
              >
                <span className="value">
                  {formatDate(statsQuery.data.lastMessage.created_at)}
                </span>
                <span className="label">Last Message Recorded</span>
              </Link>
            )}
            {statsQuery.data.lastPlay != null && (
              <Link
                className="info-block"
                to={`/messages/${statsQuery.data.lastPlay.message_id}`}
              >
                <span className="value">
                  {formatDate(statsQuery.data.lastPlay.played_at)}
                </span>
                <span className="label">Last Message Played</span>
              </Link>
            )}
            <div className="info-block">
              <span className="value">{statsQuery.data.totalListens}</span>
              <span className="label">Total Listens</span>
            </div>
          </>
        )}
        {systemQuery.data != null && (
          <>
            <div className="info-block">
              <span className="value">
                {DateTime.fromMillis(systemQuery.data.time.current).toFormat(
                  'M/dd t'
                )}
              </span>
              <span className="label">Current Time</span>
            </div>
            <div className="info-block">
              <span className="value">
                {Duration.fromMillis(
                  systemQuery.data.time.uptime * 1000
                ).toFormat(`d'd' h'h' m'm'`)}
              </span>
              <span className="label">Uptime</span>
            </div>
            {largestDisk != null && (
              <div className="info-block">
                <span className="value">{largestDisk.use}%</span>
                <span className="label">Disk Usage</span>
              </div>
            )}
            <div className="info-block">
              <span className="value">
                {(systemQuery.data.memory.active / 1024 / 1024 / 1024).toFixed(
                  2
                )}
                GB
              </span>
              <span className="label">Memory Usage</span>
            </div>
          </>
          
        )}
        <Link
          className="info-block"
          to={`/api/logs/telephone`}
        ><span className="value">Telephone Log</span></Link>
      </div>
    </main>
  );
};
