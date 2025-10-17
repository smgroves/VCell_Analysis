clear
close all hidden
warning off
set(groot, 'defaultAxesTickLabelInterpreter','none')
set(groot, 'defaultColorbarTickLabelInterpreter','none')
set(groot, 'defaultGraphplotInterpreter','none')
set(groot, 'defaultLegendInterpreter','none')
set(groot, 'defaultTextInterpreter','none')

ClinSignatureTable = readtable(strcat(pwd,'/Table_1.XLS'));
TCGABLBCTable = readtable(strcat(pwd,'/TCGA_TNBC_RNAseq.txt'));
%Normalize to TPM
TCGABLBCTable{:,2:width(TCGABLBCTable)} = TCGABLBCTable{:,2:width(TCGABLBCTable)} ./ ...
    sum(TCGABLBCTable{:,2:width(TCGABLBCTable)}) * 1e6;

%% Extract OncotypeDX genes
OncotypeDXgenes = ClinSignatureTable(~strcmp(ClinSignatureTable{:,1},''),1);
%Fix names
OncotypeDXgenes{strcmp(OncotypeDXgenes.Variables,'GUS'),1} = {'GUSB'};
OncotypeDXgenes{strcmp(OncotypeDXgenes.Variables,'HER2'),1} = {'ERBB2'};
OncotypeDXgenes{strcmp(OncotypeDXgenes.Variables,'Ki67'),1} = {'MKI67'};
OncotypeDXgenes{strcmp(OncotypeDXgenes.Variables,'RPLPO'),1} = {'RPLP0'};
OncotypeDXgenes{strcmp(OncotypeDXgenes.Variables,'STK15'),1} = {'AURKA'};
OncotypeDXgenes{strcmp(OncotypeDXgenes.Variables,'TRFC'),1} = {'TFRC'};

OncotypeDXTCGA = zeros(height(OncotypeDXgenes),width(TCGABLBCTable)-1); %Preallocate array
for i = 1:height(OncotypeDXgenes)
    OncotypeDXTCGA(i,:) = TCGABLBCTable{startsWith(TCGABLBCTable{:,1}, ...
        strcat(OncotypeDXgenes{i,1},'|')),2:width(TCGABLBCTable)};
end
OncotypeDXTable = [OncotypeDXgenes array2table(OncotypeDXTCGA, ...
    'VariableNames',{TCGABLBCTable.Properties.VariableNames{2:width(TCGABLBCTable)}})];
OncotypeDXTable = rows2vars(OncotypeDXTable,'VariableNamesSource', ...
    'OncotypeDX');
OncotypeDXTable.Properties.VariableNames(1) = {'TCGA_identifier'};

%% Extract Mammaprint genes
Mammaprintgenes = ClinSignatureTable(~strcmp(ClinSignatureTable{:,2},''),2);
%Fix names and omit unassigned identifiers
Mammaprintgenes(strcmp(Mammaprintgenes.Variables,'AA555029_RC'),:) = [];
Mammaprintgenes{strcmp(Mammaprintgenes.Variables,'AYTL2'),1} = {'LPCAT1'};
Mammaprintgenes{strcmp(Mammaprintgenes.Variables,'KNTC2'),1} = {'NDC80'};
Mammaprintgenes{strcmp(Mammaprintgenes.Variables,'LGP2'),1} = {'DHX58'};
Mammaprintgenes(strcmp(Mammaprintgenes.Variables,'LOC100131053'),:) = [];
Mammaprintgenes(strcmp(Mammaprintgenes.Variables,'LOC100288906'),:) = [];
Mammaprintgenes(strcmp(Mammaprintgenes.Variables,'LOC730018'),:) = [];
Mammaprintgenes{strcmp(Mammaprintgenes.Variables,'QSCN6L1'),1} = {'QSOX2'};
Mammaprintgenes{strcmp(Mammaprintgenes.Variables,'ZNF533'),1} = {'ZNF385B'};

MammaprintTCGA = zeros(height(Mammaprintgenes),width(TCGABLBCTable)-1); %Preallocate array
for i = 1:height(Mammaprintgenes)
    MammaprintTCGA(i,:) = TCGABLBCTable{startsWith(TCGABLBCTable{:,1}, ...
        strcat(Mammaprintgenes{i,1},'|')),2:width(TCGABLBCTable)};
end
MammaprintTable = [Mammaprintgenes array2table(MammaprintTCGA, ...
    'VariableNames',{TCGABLBCTable.Properties.VariableNames{2:width(TCGABLBCTable)}})];
MammaprintTable = rows2vars(MammaprintTable,'VariableNamesSource', ...
    'Mammaprint');
MammaprintTable.Properties.VariableNames(1) = {'TCGA_identifier'};

%% Extract Prosigna genes
Prosignagenes = ClinSignatureTable(~strcmp(ClinSignatureTable{:,3},''),3);
%Fix names and omit unassigned identifiers
Prosignagenes(strcmp(Prosignagenes.Variables,'AA555029_RC'),:) = [];
Prosignagenes{strcmp(Prosignagenes.Variables,'CDCA1'),1} = {'NUF2'};
Prosignagenes{strcmp(Prosignagenes.Variables,'KNTC2'),1} = {'NDC80'};

ProsignaTCGA = zeros(height(Prosignagenes),width(TCGABLBCTable)-1); %Preallocate array
for i = 1:height(Prosignagenes)
    ProsignaTCGA(i,:) = TCGABLBCTable{startsWith(TCGABLBCTable{:,1}, ...
        strcat(Prosignagenes{i,1},'|')),2:width(TCGABLBCTable)};
end
ProsignaTable = [Prosignagenes array2table(ProsignaTCGA, ...
    'VariableNames',{TCGABLBCTable.Properties.VariableNames{2:width(TCGABLBCTable)}})];
ProsignaTable = rows2vars(ProsignaTable,'VariableNamesSource', ...
    'Prosigna_PAM50');
ProsignaTable.Properties.VariableNames(1) = {'TCGA_identifier'};

%% Extract model species genes

ModelSpecies = {'PLK1'; 'H2A'; 'GSG2'; 'H3'; 'AURKB'; 'INCENP'; 'BIRC5'; ...
    'CDCA8'; 'TTK'; 'NDC80'; 'KNL1'; 'BUB1'; 'SGO1'}; %Gene names for species in the CSN model
ModelTCGA = zeros(height(ModelSpecies),width(TCGABLBCTable)-1); %Preallocate array
for i = [1 3 5:10 12] %Find easy ones
    ModelTCGA(i,:) = TCGABLBCTable{startsWith(TCGABLBCTable{:,1}, ...
        strcat(ModelSpecies{i,1},'|')),2:width(TCGABLBCTable)};
end
%Use old gene name for KNL1 and SGO1
ModelTCGA(11,:) = TCGABLBCTable{startsWith(TCGABLBCTable{:,1},strcat('CASC5','|')),2:width(TCGABLBCTable)};
ModelTCGA(13,:) = TCGABLBCTable{startsWith(TCGABLBCTable{:,1},strcat('SGOL1','|')),2:width(TCGABLBCTable)};
%Aggregate H2A and H3 species
ModelTCGA(2,:) = sum(TCGABLBCTable{contains(TCGABLBCTable{:,1},'H2A') & ...
    ~(contains(TCGABLBCTable{:,1},'RNASEH2A') | contains(TCGABLBCTable{:,1}, ...
    'USH2A')),2:width(TCGABLBCTable)});
ModelTCGA(4,:) = sum(TCGABLBCTable{contains(TCGABLBCTable{:,1},'H3F3') | ...
    contains(TCGABLBCTable{:,1},'HIST1H3') | contains(TCGABLBCTable{:,1}, ...
    'HIST2H3') | contains(TCGABLBCTable{:,1},'HIST3H3'),2:width(TCGABLBCTable)});

%Rename model species that also appear in gene signatures
ModelSpecies(strcmp(ModelSpecies,'BIRC5')) = {'BIRC5_model'};
ModelSpecies(strcmp(ModelSpecies,'NDC80')) = {'NDC80_model'};
ModelTable = [cell2table(ModelSpecies,'VariableNames',{'Model_species'}) array2table(ModelTCGA, ...
    'VariableNames',{TCGABLBCTable.Properties.VariableNames{2:width(TCGABLBCTable)}})];
ModelTable = rows2vars(ModelTable,'VariableNamesSource', ...
    'Model_species');
ModelTable.Properties.VariableNames(1) = {'TCGA_identifier'};

%% Fit linear models
for i = 2:width(ModelTable)
    temp = fitlm([OncotypeDXTable(:,2:width(OncotypeDXTable)) ModelTable(:,i)], ...
        'RobustOpts','off');
    OncotypeDXlm{i-1} = temp;
    temp = fitlm([MammaprintTable(:,2:width(MammaprintTable)) ModelTable(:,i)], ...
        'RobustOpts','off');
    Mammaprintlm{i-1} = temp;
    temp = fitlm([ProsignaTable(:,2:width(ProsignaTable)) ModelTable(:,i)], ...
        'RobustOpts','off');
    Prosignalm{i-1} = temp;
end
clear temp

%% Read in CIN scores and map to TCGA identifiers
CINTable = readtable(strcat(pwd,'/1-s2.0-S2211124718307009-mmc2.xlsx'));
colorscale = cool;
CINscore = zeros(width(TCGABLBCTable)-1,1); %Preallocate array
TCGAcolorscale = zeros(width(TCGABLBCTable)-1,3); %Preallocate array
TCGAmarkersize = zeros(width(TCGABLBCTable)-1); %Preallocate array
for i = 2:width(TCGABLBCTable)
    if any(contains(CINTable.TumorID, ...
        TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}) ...
        -3)))
        CINscore(i-1) = CINTable{contains(CINTable.TumorID, ...
            TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}) ...
            -3)),2};
    else
        CINscore(i-1) = nan;
    end
end
for i = 1:length(CINscore)
    if ~isnan(CINscore(i))
        TCGAcolorscale(i,:) = colorscale(round((CINscore(i)-min(CINscore))/(max(CINscore)-min(CINscore)) ...
            *(height(colorscale)-1))+1,:);
        TCGAmarkersize(i) = 10;
    else
        TCGAcolorscale(i,:) = [200 200 200]/255; %Assign unknown CIN scores to gray
        TCGAmarkersize(i) = 6;
    end
end

%% Compare calibration fits
figure(1)
for i = 1:height(ModelSpecies)
    subplot(3,5,i)
    hold on
    for j = 1:height(OncotypeDXTable)
        plot(predict(OncotypeDXlm{i},OncotypeDXTable{j,2:width(OncotypeDXTable)}), ...
            ModelTable{j,i+1},'.','Color',TCGAcolorscale(j,:),'MarkerSize',TCGAmarkersize(j))
    end
    title(ModelSpecies{i})
    xlabel('Predicted')
    ylabel('Measured')
    axis([0 max([predict(OncotypeDXlm{i},OncotypeDXTable{:,2:width(OncotypeDXTable)}); ...
        ModelTable{:,i+1}]) 0 max([predict(OncotypeDXlm{i},OncotypeDXTable{:, ...
        2:width(OncotypeDXTable)});ModelTable{:,i+1}])])
end
sgtitle('CIN scores overlaid on regression model using OncotypeDX')
figure(2)
for i = 1:height(ModelSpecies)
    subplot(3,5,i)
    hold on
    for j = 1:height(MammaprintTable)
        plot(predict(Mammaprintlm{i},MammaprintTable{j,2:width(MammaprintTable)}), ...
            ModelTable{j,i+1},'.','Color',TCGAcolorscale(j,:),'MarkerSize',TCGAmarkersize(j))
    end
    title(ModelSpecies{i})
    xlabel('Predicted')
    ylabel('Measured')
    axis([0 max([predict(Mammaprintlm{i},MammaprintTable{:,2:width(MammaprintTable)}); ...
        ModelTable{:,i+1}]) 0 max([predict(Mammaprintlm{i},MammaprintTable{:, ...
        2:width(MammaprintTable)});ModelTable{:,i+1}])])
end
sgtitle('CIN scores overlaid on regression model using Mammaprint')
figure(3)
for i = 1:height(ModelSpecies)
    subplot(3,5,i)
    hold on
    for j = 1:height(ProsignaTable)
        plot(predict(Prosignalm{i},ProsignaTable{j,2:width(ProsignaTable)}), ...
            ModelTable{j,i+1},'.','Color',TCGAcolorscale(j,:),'MarkerSize',TCGAmarkersize(j))
    end
    title(ModelSpecies{i})
    xlabel('Predicted')
    ylabel('Measured')
    axis([0 max([predict(Prosignalm{i},ProsignaTable{:,2:width(ProsignaTable)}); ...
        ModelTable{:,i+1}]) 0 max([predict(Prosignalm{i},ProsignaTable{:, ...
        2:width(ProsignaTable)});ModelTable{:,i+1}])])
end
sgtitle('CIN scores overlaid on regression model using Prosigna')

%% Read in CSN modeling outputs and map to TCGA identifiers
CSNTable = readtable(strcat(pwd,'/fold-enrichment.xlsx'));
CSNscores = zeros(width(TCGABLBCTable)-1,4); %Preallocate array
CSNcolorscale = zeros(width(TCGABLBCTable)-1,3,4); %Preallocate array
CSNmarkersize = zeros(width(TCGABLBCTable)-1,4); %Preallocate array
for i = 2:width(TCGABLBCTable)
    if any(contains(CSNTable.TCGA_ID, ...
        TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}))))
        CSNscores(i-1,:) = CSNTable{contains(CSNTable.TCGA_ID, ...
            TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}) ...
            -3)),[6:8 10]}; %Ignore x4_Y_enrich_ratio (no dynamic range) and x6_X_enrich_ratio (redundant with x2_Max_enrich)
    else
        CSNscores(i-1,:) = nan;
    end
end
for i = 1:length(CSNscores)
    if ~any(isnan(CSNscores(i,:)))
        for j = 1:4
            CSNcolorscale(i,:,j) = colorscale(round((CSNscores(i,j)-min(CSNscores(:,j)))/(max(CSNscores(:,j))-min(CSNscores(:,j))) ...
                *(height(colorscale)-1))+1,:);
            CSNmarkersize(i,j) = 10;
        end
    else
        CSNcolorscale(i,:,j) = [200 200 200]/255; %Assign unknown CSN scores to gray
        CSNmarkersize(i,j) = 6;
    end
end

%% Compare calibration fits for Mammaprint only
for k = 1:4
    figure(k+3)
    for i = 1:height(ModelSpecies)
        subplot(3,5,i)
        hold on
        for j = 1:height(MammaprintTable)
            plot(predict(Mammaprintlm{i},MammaprintTable{j,2:width(MammaprintTable)}), ...
                ModelTable{j,i+1},'.','Color',CSNcolorscale(j,:,k),'MarkerSize',CSNmarkersize(j,k))
        end
        title(ModelSpecies{i})
        xlabel('Predicted')
        ylabel('Measured')
        axis([0 max([predict(Mammaprintlm{i},MammaprintTable{:,2:width(MammaprintTable)}); ...
            ModelTable{:,i+1}]) 0 max([predict(Mammaprintlm{i},MammaprintTable{:, ...
            2:width(MammaprintTable)});ModelTable{:,i+1}])])
    end
    switch k
        case 1
            sgtitle(sprintf('Fold enrichment at the inner centromere\noverlaid on regression model using Mammaprint'))
        case 2
            sgtitle(sprintf('Inner centromere / max CPC\noverlaid on regression model using Mammaprint'))
        case 3
            sgtitle(sprintf('Fold enrichment along vertical axis\noverlaid on regression model using Mammaprint'))
        case 4
            sgtitle(sprintf('Fold enrichment along horizontal axis\noverlaid on regression model using Mammaprint'))
    end
end

%% Use CSN model outputs to predict CIN
%Identify 15 most variable genes from Mammaprint (16 parameters)
MammaprintVarSort = sort(var(MammaprintTable{:,2:width(MammaprintTable)}),'descend');
MammaprintTop15 = [false (var(MammaprintTable{:,2:width(MammaprintTable)}) >= MammaprintVarSort(15))];
MammaprintCINlm = fitlm(MammaprintTable{:,MammaprintTop15},CINscore,'linear');
%Use linear model for TCGA CSN genes (14 parameters)
TCGACSNCINlm = fitlm(ModelTable{:,2:width(ModelTable)},CINscore,'linear');
%Use interactions and quadratic model for CSN scores (15 parameters)
CSNCINlm = fitlm(CSNscores,CINscore,'quadratic');

%Calibration plot
figure(8)
subplot(1,3,1)
plot(predict(MammaprintCINlm,MammaprintTable{:,MammaprintTop15}),CINscore,'.')
xlabel('Predicted CIN score from Mammaprint genes')
ylabel('Measured CIN score')
title('Calibrating CIN score vs. Mammaprint genes')
axis([0.16 0.25 0.16 0.25])
subplot(1,3,2)
plot(predict(TCGACSNCINlm,ModelTable{:,2:width(ModelTable)}),CINscore,'.')
xlabel('Predicted CIN score from CSN genes')
ylabel('Measured CIN score')
title('Calibrating CIN score vs. CSN genes')
axis([0.16 0.25 0.16 0.25])
subplot(1,3,3)
plot(predict(CSNCINlm,CSNscores),CINscore,'.')
xlabel('Predicted CIN score from model outputs')
ylabel('Measured CIN score')
title('Calibrating CIN score vs. model outputs')
axis([0.16 0.25 0.16 0.25])

%Category boxplot
CINpred = [predict(MammaprintCINlm,MammaprintTable{:,MammaprintTop15}) ...
    predict(TCGACSNCINlm,ModelTable{:,2:width(ModelTable)}) predict(CSNCINlm,CSNscores)];
CINgrp = zeros(length(CINpred),3); %Preallocate array
for i = 1:length(CINpred)
    for j = 1:width(CINpred)
        if CINpred(i,j) < 0.195
            CINgrp(i,j) = 0;
        elseif CINpred(i,j) < 0.205
            CINgrp(i,j) = 1;
        else
            CINgrp(i,j) = 2;
        end
    end
end
figure(9)
for j = 1:width(CINpred)
    subplot(1,3,j)
    boxplot(CINscore,CINgrp(:,j),'labels',{'Low' 'Mid' 'High'})
    xlabel('Predicted CIN group')
    ylabel('CIN score')
    switch j
        case 1
            title('Classified by top 15 Mammaprint genes')
        case 2
            title('Classified by CSN genes')
        case 3
            title('Classified by CSN model outputs')
    end
    text(0.85,0.195,sprintf('n = %0.2d',sum(CINgrp(:,j) == 0)))
    text(1.85,0.205,sprintf('n = %0.2d',sum(CINgrp(:,j) == 1)))
    text(2.85,0.21,sprintf('n = %0.2d',sum(CINgrp(:,j) == 2)))
end