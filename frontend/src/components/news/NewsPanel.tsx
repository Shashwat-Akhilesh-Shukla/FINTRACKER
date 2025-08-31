// src/components/news/NewsPanel.tsx
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  Avatar,
  Divider,
  IconButton,
  TextField,
  InputAdornment
} from '@mui/material';
import { Search, Refresh } from '@mui/icons-material';
import { useNewsData } from '../../hooks/useNewsData';

interface NewsItemProps {
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  imageUrl?: string;
}

const NewsItem: React.FC<NewsItemProps> = ({
  title,
  summary,
  source,
  publishedAt,
  sentiment,
  imageUrl
}) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      default: return 'default';
    }
  };

  return (
    <>
      <ListItem sx={{ px: 0, py: 2 }}>
        <Box sx={{ width: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            {imageUrl && (
              <Avatar
                src={imageUrl}
                variant="rounded"
                sx={{ width: 60, height: 60 }}
              />
            )}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  lineHeight: 1.3,
                  mb: 1,
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                {title}
              </Typography>
              <Typography
                variant="body2"
                color="textSecondary"
                sx={{
                  mb: 1,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                {summary}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  {source} • {new Date(publishedAt).toLocaleDateString()}
                </Typography>
                <Chip
                  label={sentiment}
                  color={getSentimentColor(sentiment) as any}
                  size="small"
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              </Box>
            </Box>
          </Box>
        </Box>
      </ListItem>
      <Divider />
    </>
  );
};

const NewsPanel: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { newsData, loading, refreshNews } = useNewsData(searchQuery);

  return (
    <Card elevation={2} sx={{ height: 'fit-content', maxHeight: '100vh', overflow: 'hidden' }}>
      <CardContent sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" fontWeight={600}>
            Market News
          </Typography>
          <IconButton onClick={refreshNews} size="small">
            <Refresh />
          </IconButton>
        </Box>
        
        <TextField
          fullWidth
          size="small"
          placeholder="Search financial news..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />
      </CardContent>
      
      <Box sx={{ maxHeight: 'calc(100vh - 200px)', overflow: 'auto' }}>
        <List sx={{ px: 2, pt: 0 }}>
          {newsData.map((news, index) => (
            <NewsItem key={index} {...news} />
          ))}
        </List>
      </Box>
    </Card>
  );
};

export default NewsPanel;
