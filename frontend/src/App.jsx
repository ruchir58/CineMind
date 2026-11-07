import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import MediaDetailsModal from './components/MediaDetailsModal';
import HomePage from './pages/HomePage';
import SmartRecommendationsPage from './pages/SmartRecommendationsPage';
import AIFinderPage from './pages/AIFinderPage';
import ExplorePage from './pages/ExplorePage';
import { fetchHealth } from './services/api';

export default function App() {
  const [currentTab, setCurrentTab] = useState('home');
  const [exploreGenre, setExploreGenre] = useState('');
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    // Health check on mount
    const checkConnection = async () => {
      try {
        const data = await fetchHealth();
        setHealthStatus(data);
      } catch (err) {
        console.warn('Backend server currently starting or offline:', err);
      }
    };
    checkConnection();
  }, []);

  const handleNavigate = (tab, params = {}) => {
    setCurrentTab(tab);
    if (params.genre) {
      setExploreGenre(params.genre);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectMedia = (media) => {
    setSelectedMedia(media);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080a0d] text-zinc-100 selection:bg-indigo-600 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={(tab) => handleNavigate(tab)}
        onSelectMedia={handleSelectMedia}
      />

      {/* Main Content Pages */}
      <main className="flex-1">
        {currentTab === 'home' && (
          <HomePage
            onNavigate={handleNavigate}
            onSelectMedia={handleSelectMedia}
          />
        )}

        {currentTab === 'smart' && (
          <SmartRecommendationsPage
            onSelectMedia={handleSelectMedia}
          />
        )}

        {currentTab === 'ai' && (
          <AIFinderPage
            onSelectMedia={handleSelectMedia}
          />
        )}

        {currentTab === 'explore' && (
          <ExplorePage
            onSelectMedia={handleSelectMedia}
            initialGenre={exploreGenre}
          />
        )}
      </main>

      {/* Global Details Modal */}
      {selectedMedia && (
        <MediaDetailsModal
          media={selectedMedia}
          onClose={() => setSelectedMedia(null)}
          onSelectMedia={handleSelectMedia}
        />
      )}

      {/* Footer */}
      <Footer onNavigate={handleNavigate} />
    </div>
  );
}

