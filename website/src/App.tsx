import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Routes, Route, Outlet, Link } from 'react-router-dom';
import { MessageList } from './routes/MessageList';
import { MessageDetails } from './routes/MessageDetails';
import { Home } from './routes/Home';

const queryClient = new QueryClient();

function Messages() {
  return <Outlet />;
}

function Container() {
  return (
    <QueryClientProvider client={queryClient}>
      <header>
        <h1>
          <Link to="/">Telephone</Link>
        </h1>
        <nav>
          <Link to="/">Home</Link> | <Link to="messages">Messages</Link>
        </nav>
      </header>

      <Outlet />
    </QueryClientProvider>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Container />}>
          <Route index element={<Home />} />
          <Route path="messages" element={<Messages />}>
            <Route path=":id" element={<MessageDetails />}></Route>
            <Route index element={<MessageList />}></Route>
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
