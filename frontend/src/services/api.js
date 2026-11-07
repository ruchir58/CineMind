import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p';

export const getPosterUrl = (posterPath, size = 'w500') => {
  if (!posterPath) {
    return 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=500&q=80';
  }
  if (posterPath.startsWith('http')) return posterPath;
  return `${TMDB_IMAGE_BASE}/${size}${posterPath.startsWith('/') ? posterPath : `/${posterPath}`}`;
};

export const getBackdropUrl = (backdropPath, size = 'original') => {
  if (!backdropPath) {
    return 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=1920&q=80';
  }
  if (backdropPath.startsWith('http')) return backdropPath;
  return `${TMDB_IMAGE_BASE}/${size}${backdropPath.startsWith('/') ? backdropPath : `/${backdropPath}`}`;
};

export const fetchHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const fetchMovies = async (params = {}) => {
  const response = await api.get('/movies', { params });
  return response.data;
};

export const fetchTvShows = async (params = {}) => {
  const response = await api.get('/tv-shows', { params });
  return response.data;
};

export const fetchMovieById = async (id) => {
  const response = await api.get(`/movies/${id}`);
  return response.data;
};

export const fetchTvById = async (id) => {
  const response = await api.get(`/tv-shows/${id}`);
  return response.data;
};

export const searchMedia = async (query) => {
  const response = await api.get('/search', { params: { query } });
  return response.data;
};

export const fetchGenres = async () => {
  const response = await api.get('/genres');
  return response.data;
};

export const fetchTrending = async (mediaType = 'all') => {
  const response = await api.get('/trending', { params: { media_type: mediaType } });
  return response.data;
};

export const fetchPopular = async (mediaType = 'all') => {
  const response = await api.get('/popular', { params: { media_type: mediaType } });
  return response.data;
};

export const fetchTopRated = async (mediaType = 'all') => {
  const response = await api.get('/top-rated', { params: { media_type: mediaType } });
  return response.data;
};

export const fetchSimilar = async (mediaType, id) => {
  const response = await api.get(`/similar/${mediaType}/${id}`);
  return response.data;
};

export const generateSmartRecommendations = async (payload) => {
  const response = await api.post('/recommendations/smart', payload);
  return response.data;
};

export const generateAIRecommendations = async (payload) => {
  const response = await api.post('/recommendations/ai', payload);
  return response.data;
};

export default api;

