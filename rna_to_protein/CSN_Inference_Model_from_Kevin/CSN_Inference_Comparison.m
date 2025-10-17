cd("/Users/smgroves/Documents/GitHub/")

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
maxvalues = [200 2500 20 3500 100 100 200 200 250 150 80 350 80];
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
    axis([0 maxvalues(i) 0 maxvalues(i)])
    axis square
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
    axis([0 maxvalues(i) 0 maxvalues(i)])
    axis square
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
    axis([0 maxvalues(i) 0 maxvalues(i)])
    axis square
end
sgtitle('CIN scores overlaid on regression model using Prosigna')

%% Read in CSN modeling outputs and map to TCGA identifiers
CSN06Table = readtable(strcat(pwd,'/kk06 fold enrichment data.csv'));
CSN06scores = zeros(width(TCGABLBCTable)-1,3); %Preallocate array
CSN12Table = readtable(strcat(pwd,'/kk12 fold enrichment data.csv'));
CSN12scores = zeros(width(TCGABLBCTable)-1,3); %Preallocate array
CSNcolorscale = zeros(width(TCGABLBCTable)-1,3,6); %Preallocate array
CSNmarkersize = zeros(width(TCGABLBCTable)-1,6); %Preallocate array
for i = 2:width(TCGABLBCTable)
    if any(contains(CSN06Table.TCGA_ID, ...
        TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}))))
        CSN06scores(i-1,:) = CSN06Table{contains(CSN06Table.TCGA_ID, ...
            TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}) ...
            -3)),[6 8 10]}; %Ignore max_enrich, y_enrich_ratio, and x_enrich_ratio (no dynamic range)
    else
        CSN06scores(i-1,:) = nan;
    end
    if any(contains(CSN12Table.TCGA_ID, ...
        TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}))))
        CSN12scores(i-1,:) = CSN12Table{contains(CSN12Table.TCGA_ID, ...
            TCGABLBCTable.Properties.VariableNames{i}(1:width(TCGABLBCTable.Properties.VariableNames{i}) ...
            -3)),[6 8 10]}; %Ignore max_enrich, y_enrich_ratio, and x_enrich_ratio (no dynamic range)
    else
        CSN12scores(i-1,:) = nan;
    end
end

CSNscores = [CSN06scores CSN12scores CSN06scores./CSN12scores]; %Include 0.6 –> 1.2 µm fold-change

for i = 1:length(CSNscores)
    if ~any(isnan(CSNscores(i,:)))
        for j = 1:width(CSNscores)
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
% for k = 1:8
%     figure(k+3)
%     for i = 1:height(ModelSpecies)
%         subplot(3,5,i)
%         hold on
%         for j = 1:height(MammaprintTable)
%             plot(predict(Mammaprintlm{i},MammaprintTable{j,2:width(MammaprintTable)}), ...
%                 ModelTable{j,i+1},'.','Color',CSNcolorscale(j,:,k),'MarkerSize',CSNmarkersize(j,k))
%         end
%         title(ModelSpecies{i})
%         xlabel('Predicted')
%         ylabel('Measured')
%         axis([0 max([predict(Mammaprintlm{i},MammaprintTable{:,2:width(MammaprintTable)}); ...
%             ModelTable{:,i+1}]) 0 max([predict(Mammaprintlm{i},MammaprintTable{:, ...
%             2:width(MammaprintTable)});ModelTable{:,i+1}])])
%     end
%     switch k
%         case 1
%             sgtitle(sprintf('Fold enrichment at the inner centromere (0.6 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 2
%             sgtitle(sprintf('Inner centromere / max CPC (0.6 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 3
%             sgtitle(sprintf('Fold enrichment along vertical axis (0.6 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 4
%             sgtitle(sprintf('Fold enrichment along horizontal axis (0.6 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 5
%             sgtitle(sprintf('Fold enrichment at the inner centromere (1.2 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 6
%             sgtitle(sprintf('Inner centromere / max CPC (1.2 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 7
%             sgtitle(sprintf('Fold enrichment along vertical axis (1.2 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%         case 8
%             sgtitle(sprintf('Fold enrichment along horizontal axis (1.2 µm kk spacing)\noverlaid on regression model using Mammaprint'))
%     end
% end

%% Use CSN model outputs to predict CIN
%Use all of Mammaprint (62 parameters)
MammaprintVarSort = sort(var(MammaprintTable{:,2:width(MammaprintTable)}),'descend');
MammaprintTopGenes = [false (var(MammaprintTable{:,2:width(MammaprintTable)}) >= MammaprintVarSort(62))];
MammaprintCINlm = fitlm(MammaprintTable{:,MammaprintTopGenes},CINscore,'linear');
MammaprintXvalPred = zeros(height(CINscore),1);
for i = 1:height(CINscore) %Leave-one-out cross-validated predictions
    MammaprintCINlmtemp = fitlm(MammaprintTable{:,MammaprintTopGenes},CINscore,'linear','exclude',i);
    MammaprintXvalPred(i) = predict(MammaprintCINlmtemp,MammaprintTable{i,MammaprintTopGenes});
end

%Use linear model for TCGA CSN genes (14 parameters)
TCGACSNCINlm = fitlm(ModelTable{:,2:width(ModelTable)},CINscore,'linear');
TCGAXvalPred = zeros(height(CINscore),1);
for i = 1:height(CINscore) %Leave-one-out cross-validated predictions
    TCGACSNCINlmtemp = fitlm(ModelTable{:,2:width(ModelTable)},CINscore,'linear','exclude',i);
    TCGAXvalPred(i) = predict(TCGACSNCINlmtemp,ModelTable{i,2:width(ModelTable)});
end

%Use interactions and quadratic model for CSN scores (28 parameters)
CSNCINlm = fitlm(CSNscores,CINscore,'quadratic');
CSNXvalPred = zeros(height(CINscore),1);
for i = 1:height(CINscore) %Leave-one-out cross-validated predictions
    CSNCINlmtemp = fitlm(CSNscores,CINscore,'quadratic','exclude',i);
    CSNXvalPred(i) = predict(CSNCINlmtemp,CSNscores(i,:));
end

%Calibration plot
figure(8)
corrinterval = [0.1 0.1; 0.1 0.13; 0.27 0.3; 0.3 0.3; 0.3 0.27; 0.13 0.1];
subplot(2,3,1)
patch(corrinterval(:,1),corrinterval(:,2),[240 240 240]/255,'LineStyle','none')
hold on
plot(predict(MammaprintCINlm,MammaprintTable{:,MammaprintTopGenes}),CINscore,'k.')
xlabel('Predicted FA score from Mammaprint genes')
ylabel('Measured FA score')
title('Calibrating FA score vs. Mammaprint genes')
hold on
axis([0.1 0.3 0.1 0.3])
text(0.11,0.28,sprintf('rho = %0.2f',corr(predict(MammaprintCINlm, ...
    MammaprintTable{:,MammaprintTopGenes}),CINscore,'rows','pairwise')))
subplot(2,3,2)
patch(corrinterval(:,1),corrinterval(:,2),[240 240 240]/255,'LineStyle','none')
hold on
plot(predict(TCGACSNCINlm,ModelTable{:,2:width(ModelTable)}),CINscore,'k.')
xlabel('Predicted FA score from CSN genes')
ylabel('Measured FA score')
title('Calibrating FA score vs. CSN genes')
axis([0.1 0.3 0.1 0.3])
subplot(2,3,3)
patch(corrinterval(:,1),corrinterval(:,2),[240 240 240]/255,'LineStyle','none')
hold on
plot(predict(CSNCINlm,CSNscores),CINscore,'k.')
xlabel('Predicted FA score from model outputs')
ylabel('Measured FA score')
title('Calibrating FA score vs. model outputs')
axis([0.1 0.3 0.1 0.3])
text(0.11,0.28,sprintf('rho = %0.2f',corr(predict(CSNCINlm,CSNscores), ...
    CINscore,'rows','pairwise')))

%Cross-validated prediction plot
subplot(2,3,4)
patch(corrinterval(:,1),corrinterval(:,2),[240 240 240]/255,'LineStyle','none')
hold on
plot(MammaprintXvalPred,CINscore,'k.')
xlabel('Predicted FA score from Mammaprint genes')
ylabel('Measured FA score')
title('Xval predicted FA score vs. Mammaprint genes')
axis([0.1 0.3 0.1 0.3])
[rhoMammaprint(1),rhoMammaprint(2)] = corr(MammaprintXvalPred,CINscore, ...
    'rows','pairwise'); %Report crossvalidated correlation
text(0.11,0.28,sprintf('rho = %0.2f\np = %0.3f',rhoMammaprint(1),rhoMammaprint(2)))
subplot(2,3,5)
patch(corrinterval(:,1),corrinterval(:,2),[240 240 240]/255,'LineStyle','none')
hold on
plot(TCGAXvalPred,CINscore,'k.')
xlabel('Predicted FA score from CSN genes')
ylabel('Measured FA score')
title('Xval predicted FA score vs. CSN genes')
axis([0.1 0.3 0.1 0.3])
subplot(2,3,6)
patch(corrinterval(:,1),corrinterval(:,2),[240 240 240]/255,'LineStyle','none')
hold on
plot(CSNXvalPred,CINscore,'k.')
xlabel('Predicted FA score from model outputs')
ylabel('Measured FA score')
title('Xval predicted FA score vs. model outputs')
axis([0.1 0.3 0.1 0.3])
[rhoCSN(1),rhoCSN(2)] = corr(CSNXvalPred,CINscore,'rows','pairwise');
text(0.11,0.28,sprintf('rho = %0.2f\np = %0.3f',rhoCSN(1),rhoCSN(2)))

