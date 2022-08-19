import React from 'react';
import { useQuery } from 'react-query';
import { Link, useParams } from 'react-router-dom';
import { API_ROOT, MESSAGES_ROOT } from '../config';
import { formatDate } from './MessageList';
import { Message } from '../types';
import AudioPlayer from 'react-h5-audio-player';

export function MessageDetails() {
  const { id } = useParams();

  const { data } = useQuery<{
    message: Message;
    previous?: Message;
    next?: Message;
  }>(`messages/${id}`, () =>
    fetch(`${API_ROOT}/message/${id}`).then((res) => res.json())
  );

  if (data == null) {
    return <></>;
  }

  return (
    <main
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1em',
        maxWidth: '50em',
        margin: '0 auto',
      }}
    >
      <header className="message__header">
        {data.previous == null ? (
          <span></span>
        ) : (
          <Link to={`../${data.previous.id}`}>⟵ Previous</Link>
        )}
        {data.next != null && <Link to={`../${data.next.id}`}>Next ⟶</Link>}
      </header>
      <section>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2>Recording #{data.message.id}</h2>
          <span>{formatDate(data.message.created_at)}</span>
        </div>
        <p>Played {data.message.play_count} times</p>
        {data.message.play_count > 0 && (
          <p>Last played at {data.message.last_played_at}</p>
        )}
      </section>
      <section>
        <img
          src={`${API_ROOT}/visualize?filename=${data.message.filename}`}
          style={{ aspectRatio: '1/4' }}
        />
      </section>
      <section>
        <AudioPlayer
          src={`${MESSAGES_ROOT}/${data.message.filename}`}
          layout="horizontal"
          customAdditionalControls={[]}
          customVolumeControls={[]}
          showJumpControls={false}
          showSkipControls={false}
        />
      </section>
    </main>
  );
}
