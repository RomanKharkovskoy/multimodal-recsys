import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, TextField, Typography, List, ListItem, ListItemText, Alert, Paper, Divider } from '@mui/material';
import RecommendIcon from '@mui/icons-material/Recommend';

export default function Recommendations() {
  const [businessId, setBusinessId] = useState('');
  const [itemIdx, setItemIdx] = useState('');
  const [k, setK] = useState(5);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleGet = async () => {
    setError('');
    setResult(null);
    try {
      const res = await axios.get(`http://localhost:8000/businesses/${businessId}/recommend/${itemIdx}?k=${k}`);
      setResult(res.data);
    } catch (e) {
      setError('Ошибка получения рекомендаций');
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Рекомендации</Typography>
      <Box display="flex" alignItems="center" gap={2}>
        <TextField label="ID бизнеса" value={businessId} onChange={e => setBusinessId(e.target.value)} sx={{ width: 140 }} />
        <TextField label="Индекс товара" value={itemIdx} onChange={e => setItemIdx(e.target.value)} sx={{ width: 140 }} />
        <TextField label="K" type="number" value={k} onChange={e => setK(Number(e.target.value))} sx={{ width: 80 }} />
        <Button variant="contained" onClick={handleGet} startIcon={<RecommendIcon />} sx={{ borderRadius: 2 }}>
          Получить
        </Button>
      </Box>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {result && (
        <Box sx={{ mt: 3 }}>
          <Typography>Товар: <b>{result.product_name}</b></Typography>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Рекомендации:</Typography>
          <List>
            {result.recommendations.map(r => (
              <ListItem key={r.index} sx={{ borderRadius: 2, mb: 1, background: '#f5f7fa', boxShadow: 1 }}>
                <ListItemText primary={r.product_name} secondary={`index: ${r.index}`} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
}
