# input frames 10, output frames 18
# I size = 180, F size = 60
python convGRU_run.py \
    --root-dir 01_Radar_data/02_numpy_files \
    --ty-list-file ty_list.xlsx \
    --result-dir 04_results/server \
    --weight-decay 0.1 --gpu 2 --input-with-grid

python convGRU_run.py \
    --root-dir 01_Radar_data/02_numpy_files \
    --ty-list-file ty_list.xlsx \
    --result-dir 04_results/server \
    --weight-decay 0.1 --gpu 2
