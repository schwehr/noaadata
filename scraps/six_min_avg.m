% Code by Val Schmidt, June 2008

function sma = six_min_avg(tides)
% A matlab script to convert 12 second tide data to an average value calculated over
% the two minute period surrounding each UTC six minute mark (:06, :12, :18, etc.)
%
% Val Schmidt
% CCOM/JHC
%
% Assumes 'tides' is a matrix having the following format:
% YYYY    MM    DD   HH   MM   SS  TIDELEVEL TIDE_UNCERTAINTY

year = 1;
mon = 2;
day = 3;
hour = 4; 
minute = 5;
sec = 6;

% This statement will find indices for the lines of data have minutes a multiple of six.
six_min_indices = find( mod( tides(:,minute), 6) == 0);
% This statement will find the index corresponding to the first line in the minute six window.
six_min_indices = six_min_indices(find( diff(six_min_indices) > 1));

five_min_indices = six_min_indices - 5;
seven_min_indices = six_min_indices + 5;

times = tides(six_min_indices,1:6);

% Handle the ends of the data set.
if five_min_indices(1) < 1
	  five_min_indices(1) = 1;
end
if seven_min_indices(end) > length(six_min_indices)
   seven_min_indices(end) = length(six_min_indices);
end

% Calculate the six-minute averages.
sma = zeros(length(six_min_indices),7);
for idx=1:length(six_min_indices)

	  sma(idx,:) =horzcat(times(idx,:), ...
			       mean(tides(five_min_indices(idx):seven_min_indices(idx),7) )); 

end
