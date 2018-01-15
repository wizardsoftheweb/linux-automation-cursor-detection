library(readr)
library(vioplot)
library(dplyr)

run_time_comparison <- read_csv("../data/run_time_comparison.csv")

pyautogui_pixel_color_py = dplyr::filter(run_time_comparison,
                                         script_name == "pyautogui-pixel-color.py")
mean(pyautogui_pixel_color_py$run_time)
median(pyautogui_pixel_color_py$run_time)
png(
  filename = "../output/violin-pyautogui-pixel-color.png",
  units = "px",
  width = 860,
  height = 558,
  pointsize = 12,
  res = 96
)
vioplot(
  pyautogui_pixel_color_py$run_time,
  names = c("pyautogui-pixel-color.py"),
  col = "deepskyblue2"
)
title("Violin Plot of Script Run Time",
      ylab = "Milliseconds")
dev.off()

xlib_color_py = dplyr::filter(run_time_comparison, script_name == "xlib-color.py")
mean(xlib_color_py$run_time)
median(xlib_color_py$run_time)
png(
  filename = "../output/violin-xlib-color.png",
  units = "px",
  width = 860,
  height = 558,
  pointsize = 12,
  res = 96
)
vioplot(xlib_color_py$run_time,
        names = c("xlib-color.py"),
        col = "deepskyblue2")
title("Violin Plot of Script Run Time",
      ylab = "Milliseconds")
dev.off()

xwd_convert_chained_py = dplyr::filter(run_time_comparison, script_name == "xwd-convert-chained.py")
mean(xwd_convert_chained_py$run_time)
median(xwd_convert_chained_py$run_time)
png(
  filename = "../output/violin-xwd-convert-chained.png",
  units = "px",
  width = 860,
  height = 558,
  pointsize = 12,
  res = 96
)
vioplot(
  xwd_convert_chained_py$run_time,
  names = c("xwd-convert-chained.py"),
  col = "deepskyblue2"
)
title("Violin Plot of Script Run Time",
      ylab = "Milliseconds")
dev.off()

xwd_convert_sh = dplyr::filter(run_time_comparison, script_name == "xwd-convert.sh")
mean(xwd_convert_sh$run_time)
median(xwd_convert_sh$run_time)
png(
  filename = "../output/violin-xwd-convert.png",
  units = "px",
  width = 860,
  height = 558,
  pointsize = 12,
  res = 96
)
vioplot(xwd_convert_sh$run_time,
        names = c("xwd-convert.sh"),
        col = "deepskyblue2")
title("Violin Plot of Script Run Time",
      ylab = "Milliseconds")
dev.off()

# All together
png(
  filename = "../output/violin-all.png",
  units = "px",
  width = 860,
  height = 558,
  pointsize = 12,
  res = 96
)
vioplot(
  pyautogui_pixel_color_py$run_time,
  xlib_color_py$run_time,
  xwd_convert_chained_py$run_time,
  xwd_convert_sh$run_time,
  names = c(
    "pyautogui-pixel-color.py",
    "xlib-color.py",
    "xwd-convert-chained.py",
    "xwd-convert.sh"
  ),
  col = "deepskyblue2"
)
title("Violin Plot of Script Run Time",
      ylab = "Milliseconds")
dev.off()
# Just the three slow ones
png(
  filename = "../output/violin-slow.png",
  units = "px",
  width = 860,
  height = 558,
  pointsize = 12,
  res = 96
)
vioplot(
  pyautogui_pixel_color_py$run_time,
  xwd_convert_chained_py$run_time,
  xwd_convert_sh$run_time,
  names = c(
    "pyautogui-pixel-color.py",
    "xwd-convert-chained.py",
    "xwd-convert.sh"
  ),
  col = "deepskyblue2"
)
title("Violin Plot of Script Run Time",
      ylab = "Milliseconds")
dev.off()