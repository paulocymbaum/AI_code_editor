'use client';

import React from 'react';
import { Provider } from 'react-redux';
import { store } from '/Users/paulocymbaum/Documents/Projects/AI_code_editor/demo/src/store/store';
import ChatSidebar from '/Users/paulocymbaum/Documents/Projects/AI_code_editor/demo/src/components/ChatSidebar';
import ChatHeader from '/Users/paulocymbaum/Documents/Projects/AI_code_editor/demo/src/components/ChatHeader';
import ChatMessageList from '/Users/paulocymbaum/Documents/Projects/AI_code_editor/demo/src/components/ChatMessageList';
import ChatInput from '/Users/paulocymbaum/Documents/Projects/AI_code_editor/demo/src/components/ChatInput';
import ChatFooter from '/Users/paulocymbaum/Documents/Projects/AI_code_editor/demo/src/components/ChatFooter';

const ChatPage = () => {
  return (
    <Provider store={store}>
      <div className="flex h-screen bg-neutral-50">
            {/* Sidebar - Hidden on mobile, visible on md+ */}
            <aside className="hidden md:flex md:w-64 lg:w-80 flex-col border-r border-neutral-200 bg-white">
              <ChatSidebar />
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
              {/* Header */}
              <header className="border-b border-neutral-200 bg-white p-4">
                <ChatHeader />
              </header>

              {/* Messages Area - Scrollable */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
                <ChatMessageList />
              </div>

              {/* Input Area */}
              <div className="border-t border-neutral-200 bg-white p-4">
                <ChatInput />
              </div>

              {/* Footer */}
              <footer className="border-t border-neutral-200 bg-neutral-50 p-2 sm:p-3">
                <ChatFooter />
              </footer>
            </main>
          </div>
    </Provider>
  );
};

export default ChatPage;
