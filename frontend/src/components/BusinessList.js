import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Typography, List, ListItem, ListItemText, IconButton, Card, CardContent, Divider, Tooltip } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddBusinessIcon from '@mui/icons-material/AddBusiness';

const API = 'http://localhost:8000/businesses';

export default function BusinessList() {
  const [businesses, setBusinesses] = useState([]);
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState(null);
  const [form, setForm] = useState({ name: '', industry: '', contact_email: '' });

  const fetchBusinesses = async () => {
    const res = await axios.get(API);
    setBusinesses(res.data);
  };

  useEffect(() => { fetchBusinesses(); }, []);

  const handleOpen = (b = null) => {
    setEdit(b);
    setForm(b ? b : { name: '', industry: '', contact_email: '' });
    setOpen(true);
  };
  const handleClose = () => setOpen(false);

  const handleSubmit = async () => {
    if (edit) {
      await axios.put(`${API}/${edit.id}`, form);
    } else {
      await axios.post(API, form);
    }
    fetchBusinesses();
    handleClose();
  };

  const handleDelete = async (id) => {
    await axios.delete(`${API}/${id}`);
    fetchBusinesses();
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Список бизнесов</Typography>
        <Button variant="contained" startIcon={<AddBusinessIcon />} onClick={() => handleOpen()} sx={{ borderRadius: 2 }}>
          Добавить
        </Button>
      </Box>
      <Divider sx={{ mb: 2 }} />
      <Box>
        {businesses.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ mt: 4 }}>
            Нет бизнесов. Добавьте первый!
          </Typography>
        )}
        <List>
          {businesses.map((b) => (
            <Card key={b.id} variant="outlined" sx={{ mb: 2, borderRadius: 3, boxShadow: 1 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2 }}>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>{b.name}</Typography>
                  <Typography variant="body2" color="text.secondary">{b.industry} | {b.contact_email}</Typography>
                </Box>
                <Box>
                  <Tooltip title="Редактировать"><IconButton onClick={() => handleOpen(b)} color="primary"><EditIcon /></IconButton></Tooltip>
                  <Tooltip title="Удалить"><IconButton onClick={() => handleDelete(b.id)} color="error"><DeleteIcon /></IconButton></Tooltip>
                </Box>
              </CardContent>
            </Card>
          ))}
        </List>
      </Box>
      <Dialog open={open} onClose={handleClose} PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle>{edit ? 'Редактировать бизнес' : 'Добавить бизнес'}</DialogTitle>
        <DialogContent>
          <TextField margin="dense" label="Название" fullWidth value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} sx={{ mb: 2 }} />
          <TextField margin="dense" label="Индустрия" fullWidth value={form.industry} onChange={e => setForm(f => ({ ...f, industry: e.target.value }))} sx={{ mb: 2 }} />
          <TextField margin="dense" label="Email" fullWidth value={form.contact_email} onChange={e => setForm(f => ({ ...f, contact_email: e.target.value }))} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Отмена</Button>
          <Button onClick={handleSubmit} variant="contained">Сохранить</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
