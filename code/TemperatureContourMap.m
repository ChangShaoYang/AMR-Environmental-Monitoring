function gpr_spatiotemporal_gif()
    % Load CSV file
    filename = 'csv_file';
    opts = detectImportOptions(filename, 'ReadVariableNames', false, 'Delimiter', ',');
    opts.VariableNames = {'TimeString', 'CoordString', 'THString'};
    T = readtable(filename, opts);
    
    n = height(T);
    Time = NaT(n,1);
    X = zeros(n,1);
    Y = zeros(n,1);
    Temp = zeros(n,1);
    
    % Parse data
    for i = 1:n
        % Parse time string to datetime
        dtStr = strtrim(T.TimeString{i});
        Time(i) = datetime(dtStr, 'InputFormat', 'yyyy/M/d HH:mm');
        
        % Parse coordinate string to x, y
        coordStr = strtrim(T.CoordString{i});
        coordVals = sscanf(coordStr, '%f,%f,%f');
        X(i) = coordVals(1);
        Y(i) = coordVals(2);
        
        % Parse temperature (ignore humidity)
        thStr = strtrim(T.THString{i});
        thVals = sscanf(thStr, '%f,%f');
        Temp(i) = thVals(1);
    end
    
    % Convert time to relative minutes
    time0 = min(Time);
    timeMins = minutes(Time - time0);
    
    % Form input data (time, x, y)
    InputData = [timeMins, X, Y];

    % Kernel parameters: lt (time scale), lx (x scale), ly (y scale)
    lt = 5;   % Time scale (minutes)
    lx = 1.0; % X scale
    ly = 1.0; % Y scale
    myKernelHandle = @(XN, XM, theta) mySpatioTemporalKernel(XN, XM, theta);
    
    % Train GPR model
    gprMdl = fitrgp(InputData, Temp, ...
        'KernelFunction', myKernelHandle, ...     
        'KernelParameters', [lt, lx, ly], ...       
        'BasisFunction', 'constant', ...
        'Sigma', 0.1, ...
        'OptimizeHyperparameters', 'none');
    
    % Define prediction time range (09:50 to 10:15, 1-minute intervals)
    t_start = datetime('2025/3/14 09:50', 'InputFormat', 'yyyy/M/d HH:mm');
    t_end = datetime('2025/3/14 10:15', 'InputFormat', 'yyyy/M/d HH:mm');
    timeVec = t_start:minutes(1):t_end;
    
    % Define spatial grid
    xMin = min(X)-1; xMax = max(X)+1;
    yMin = min(Y)-1; yMax = max(Y)+1;
    [xq, yq] = meshgrid(linspace(xMin, xMax, 50), linspace(yMin, yMax, 50));
    
    gifFilename = 'TemperatureContourMap.gif';
    for k = 1:length(timeVec)
        % Convert time to relative minutes
        tQuery = minutes(timeVec(k) - time0);
        gridPoints = [repmat(tQuery, numel(xq), 1), xq(:), yq(:)];
        
        % Predict temperature
        [tempPred, ~] = predict(gprMdl, gridPoints);
        tempPredGrid = reshape(tempPred, size(xq));
        
        % Create hidden figure
        fig = figure('visible', 'off');
        surf(xq, yq, tempPredGrid);
        shading interp;
        colormap jet;
        colorbar;
        zlim([15 40]);
        caxis([15 40]);
        xlabel('X axis');
        ylabel('Y axis');
        zlabel('Temperature (°C)');
        title(sprintf('Temperature Distribution at %s', datestr(timeVec(k), 'yyyy/mm/dd HH:MM')));
        
        % Mark 6 representative points
        [rows, cols] = size(xq);
        selectedPoints = [round(rows/4), round(cols/4);
                          round(rows/4), round(3*cols/4);
                          round(rows/2), round(cols/4);
                          round(3*rows/4), round(cols/4);
                          round(3*rows/4), round(3*cols/4);
                          round(rows/2), round(3*cols/4)];
        hold on;
        for idx = 1:size(selectedPoints,1)
            r = selectedPoints(idx,1);
            c = selectedPoints(idx,2);
            x_val = xq(r,c);
            y_val = yq(r,c);
            temp_val = tempPredGrid(r,c);
            textZ = temp_val + 5;
            text(x_val, y_val, textZ, sprintf('%.1f', temp_val), ...
                'FontSize', 10, 'Color', 'k', 'HorizontalAlignment', 'center');
        end
        hold off;
        
        % Save frame to GIF
        frame = getframe(fig);
        im = frame2im(frame);
        [imind, cm] = rgb2ind(im, 256);
        if k == 1
            imwrite(imind, cm, gifFilename, 'gif', 'LoopCount', inf, 'DelayTime', 0.6);
        else
            imwrite(imind, cm, gifFilename, 'gif', 'WriteMode', 'append', 'DelayTime', 0.6);
        end
        close(fig);
    end
end

function K = mySpatioTemporalKernel(XN, XM, theta)
    % Inputs: XN, XM (Nx3, Mx3 matrices), theta = [lt, lx, ly]
    lt = theta(1); % Time scale
    lx = theta(2); % X scale
    ly = theta(3); % Y scale

    timeDist = pdist2(XN(:,1), XM(:,1)).^2 / lt^2;
    xDist = pdist2(XN(:,2), XM(:,2)).^2 / lx^2;
    yDist = pdist2(XN(:,3), XM(:,3)).^2 / ly^2;

    totalDist = timeDist + xDist + yDist;
    K = exp(-totalDist);
end