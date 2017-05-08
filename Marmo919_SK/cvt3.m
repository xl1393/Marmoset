%file = fopen('filelist.txt');

file=fileread('filelist.txt');
c=strsplit(file,'\n');

for i =161:240
     line=char(c(i));
     display(line);
     img=imread(line(1:length(line)));
     save(strcat(line(55:length(line)-4),'.mat'),'img','-V7.3');
end

 
