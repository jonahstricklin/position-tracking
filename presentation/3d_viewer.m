% Show graph of Webcam movement
x_webcam = prerecwebcampositionlog.VarName1;
y_webcam = prerecwebcampositionlog.VarName2;
z_webcam = prerecwebcampositionlog.VarName3;
for index = 1:795
    subplot(1, 2, 1)
    plot3(x(1:index), y(1:index), z(1:index), "ro"); grid on;
    title("Webcam")
    axis([-60 30 -60 30 0 80])
    pause(0.00);
end

% Show graph of RPI camera movement
x_rpi = prerecrpipositionlog.x;
y_rpi = prerecrpipositionlog.y;
z_rpi = prerecrpipositionlog.z;
for index = 1:510
    subplot(1, 2, 2)
    plot3(x_rpi(1:index), y_rpi(1:index), z_rpi(1:index), "bo"); grid on;
    title("RPI Camera")
    axis([-6 8 -10 6 0 16])
    pause(0.00);
end