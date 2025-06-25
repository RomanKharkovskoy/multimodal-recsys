import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, TextField, Typography, Alert, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

export default function DataUpload() {
  const [businessId, setBusinessId] = useState('');
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    if (!businessId || !file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post(`http://localhost:8000/businesses/${businessId}/upload-data`, formData);
      setStatus('Файл успешно загружен!');
    } catch (e) {
      setStatus('Ошибка загрузки файла');
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Загрузка данных для бизнеса</Typography>
      <Box display="flex" alignItems="center" gap={2}>
        <TextField label="ID бизнеса" value={businessId} onChange={e => setBusinessId(e.target.value)} sx={{ width: 180 }} />
        <Button
          variant="outlined"
          component="label"
          startIcon={<CloudUploadIcon />}
          sx={{ borderRadius: 2 }}
        >
          Выбрать файл
          <input type="file" accept=".gz,.jsonl" hidden onChange={e => setFile(e.target.files[0])} />
        </Button>
        <Button variant="contained" onClick={handleUpload} sx={{ borderRadius: 2 }}>
          Загрузить
        </Button>
      </Box>
      {file && <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>Файл: {file.name}</Typography>}
      {status && <Alert severity={status.includes('успешно') ? 'success' : 'error'} sx={{ mt: 2 }}>{status}</Alert>}
    </Paper>
  );
}
