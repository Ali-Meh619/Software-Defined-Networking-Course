%frequency selective_Fading
s.sr = 30.72e6;
s.d = [0 10 20 30 100]/s.sr;
s.pg = [0 -3 -6 -8 -17.2];
s.do=0;
%%

[tx_FSF,rx_FSF,ber,numBits]=channel_effect_selective(11,5e7,5e7,6,3,s);

%%
%Flat_Fading

q.sr = 30.72e6;
q.d = [0 0 0 0 0]/s.sr;
q.pg = [0 -3 -6 -8 -17.2];
q.do=0;
%%
[tx_FF,rx_FF,ber,numBits]=channel_effect_flat(11,5e7,5e7,6,3,q);


%%

function indices = lteIntrlvrIndices(blkLen)

%[f1, f2] = getf1f2(blkLen);
f1=31;
f2=64;

Idx = (0:blkLen-1).';
indices = mod(f1*Idx + f2*Idx.^2, blkLen) + 1;
end


function y=Modulator(u, Mode)


QPSK = comm.PSKModulator(4, 'BitInput', true, ...
'PhaseOffset', pi/4, 'SymbolMapping', 'Custom', ...
'CustomSymbolMapping', [0 2 3 1]);

QAM16 = comm.RectangularQAMModulator(16, 'BitInput',true,...
'NormalizationMethod','Average power','SymbolMapping','Custom',...
'CustomSymbolMapping',[11 10 14 15 9 8 12 13 1 0 4 5 3 2 6 7]);

QAM64 = comm.RectangularQAMModulator('ModulationOrder',64,'BitInput',true);



switch Mode
case 1
y=step(QPSK, u);
case 2
y=step(QAM16, u);
case 3
y=step(QAM64, u);
end

end

function y=DemodulatorSoft(u, Mode, NoiseVar)

QPSK = comm.PSKDemodulator(...
'ModulationOrder', 4, ...
'BitOutput', true, ...
'PhaseOffset', pi/4, 'SymbolMapping', 'Custom', ...
'CustomSymbolMapping', [0 2 3 1],...
'DecisionMethod', 'Approximate log-likelihood ratio', ...
'VarianceSource', 'Input port');

QAM16 = comm.RectangularQAMDemodulator(...
'ModulationOrder', 16, ...
'BitOutput', true, ...
'NormalizationMethod', 'Average power', 'SymbolMapping', 'Custom', ...
'CustomSymbolMapping', [11 10 14 15 9 8 12 13 1 0 4 5 3 2 6 7],...
'DecisionMethod', 'Approximate log-likelihood ratio', ...
'VarianceSource', 'Input port');
QAM64 = comm.RectangularQAMDemodulator(...
'ModulationOrder', 64, ...
'BitOutput', true, ...
'NormalizationMethod', 'Average power', 'SymbolMapping', 'Custom', ...
'CustomSymbolMapping', ...
[47 46 42 43 59 58 62 63 45 44 40 41 57 56 60 61 37 36 32 33 ...
49 48 52 53 39 38 34 35 51 50 54 55 7 6 2 3 19 18 22 23 5 4 0 1 ...
17 16 20 21 13 12 8 9 25 24 28 29 15 14 10 11 27 26 30 31],...
'DecisionMethod', 'Approximate log-likelihood ratio', ...
'VarianceSource', 'Input port');


switch Mode
case 1
y=step(QPSK, u, NoiseVar);
case 2
y=step(QAM16,u, NoiseVar);
case 3
y=step(QAM64, u, NoiseVar);
otherwise
error('Invalid Modulation Mode. Use {1,2, or 3}');
end
end

function y=TurboEncoder(u, lteIntrlvrIndices)
%#codegen

Turbo = comm.TurboEncoder('TrellisStructure', poly2trellis(4, [13 15], 13), ...
'InterleaverIndicesSource','Input port');

y=step(Turbo, u, lteIntrlvrIndices);
end

function y=TurboDecoder(u, lteIntrlvrIndices, maxIter)

Turbo = comm.TurboDecoder('TrellisStructure', poly2trellis(4, [13 15], 13),...
'InterleaverIndicesSource','Input port', ...
'NumIterations', maxIter);

y=step(Turbo, u, lteIntrlvrIndices);
end


function [y, flag, iters]=TurboDecoder_crc(u,lteIntrlvrIndices,m)
%#codegen
MAXITER=m;

Turbo = commLTETurboDecoder('InterleaverIndicesSource', 'Input port', ...
'MaximumIterations', MAXITER);

[y, flag, iters] = step(Turbo, u, lteIntrlvrIndices);

end

function y = CbCRCDetector(u)
%#codegen

hTBCRC = comm.CRCDetector('Polynomial', [1 1 zeros(1, 16) 1 1 0 0 0 1 1]);

% Transport block CRC generation
y = step(hTBCRC, u);
end

function y = CbCRCGenerator(u)

hTBCRCGen = comm.CRCGenerator('Polynomial',[1 1 zeros(1, 16) 1 1 0 0 0 1 1]);

% Transport block CRC generation
y = step(hTBCRCGen, u);
end

function y = cd(u)
%#codegen

hTBCRC = comm.CRCDetector('Polynomial', [1 1 zeros(1, 16) 1 1 0 0 0 1 1]);

% Transport block CRC generation
y = step(hTBCRC, u);
end

function y=siso_flat(x,s)

mimochannel = comm.MIMOChannel(...
    'SampleRate',s.sr, ...
    'PathDelays',s.d, ...
    'AveragePathGains',s.pg, ...
    'MaximumDopplerShift',s.do, ...
    'TransmitCorrelationMatrix', eye(1), ...
    'ReceiveCorrelationMatrix', eye(1), ...
    'PathGainsOutputPort', false, ...
    'NormalizePathGains', true, ....
    'NormalizeChannelOutputs', true);

y=mimochannel(x);

end

function y=siso_selective(x,s)

mimochannel_1 = comm.MIMOChannel(...
    'SampleRate',s.sr, ...
    'PathDelays',s.d, ...
    'AveragePathGains',s.pg, ...
    'MaximumDopplerShift',s.do, ...
    'TransmitCorrelationMatrix', eye(1), ...
    'ReceiveCorrelationMatrix', eye(1), ...
    'PathGainsOutputPort', false, ...
    'NormalizePathGains', true, ....
    'NormalizeChannelOutputs', true);

y=mimochannel_1(x);

end


function [tx,rx,ber, numBits]=channel_effect_flat(EbNo, maxNumErrs, maxNumBits,m,k,ss)

FRM=2048; % Size of bit frame
Kplus=FRM+24;
BitError = comm.ErrorRate;
AWGN = comm.AWGNChannel;
Indices = lteIntrlvrIndices(Kplus);

if k==1
    a1={'QPSK'};
    a2='QPSK';
    s.Modulation=a2;
    s.Nlayers=1;
    s.TxScheme='Port0';
    s.NIR=0;
    s.NSoftbits=0;
    s.DuplexMode='FDD';
    s.TDDConfig=0;
    
    
elseif k==2
    
    a1={'16QAM'};
    a2='16QAM';
    s.Modulation=a2;
    s.Nlayers=1;
    s.TxScheme='Port0';
    s.NIR=0;
    s.NSoftbits=0;
    s.DuplexMode='FDD';
    s.TDDConfig=0;
    
elseif k==3
    
    a1={'64QAM'};
    a2='64QAM';
    s.Modulation=a2;
    s.Nlayers=1;
    s.TxScheme='Port0';
    s.NIR=0;
    s.NSoftbits=0;
    s.DuplexMode='FDD';
    s.TDDConfig=0;
    
end


maxIter=6;
CodingRate=Kplus/(3*Kplus+12);
snr = EbNo;
noiseVar = 10.^(-snr/10);
Hist=dsp.Histogram('LowerLimit', 1, 'UpperLimit', maxIter, 'NumBins', maxIter,'RunningHistogram', true);

%xx=ceil((FRM+4)/rr);

numErrs = 0; numBits = 0; nS=0;

rx=[];
tx=[];
while ((numErrs < maxNumErrs) && (numBits < maxNumBits))
% Transmitter
u = randi([0 1], FRM,1); % Randomly generated input bits
%data= CbCRCGenerator(u); % Transport block CRC code
q = lteTurboEncode(u);

%t1=lteRateMatchTurbo(q,xx,0,s);


t2 =lteSymbolModulate(q,a1);


% Channel
g=siso_flat(t2,ss);

c0 = awgn(g,snr); % AWGN channel
% Receiver



r0 = lteSymbolDemodulate(c0,a2,'Soft');

%r1 = lteRateRecoverTurbo(r0,2400,0,s);
%a=cell2mat(r1);
%a=double(a);
y = lteTurboDecode(r0,m);
y=double(y);
% Turbo Decoder
%z=cd(y)
% Measurements
numErrs = numErrs + sum(~(y)==u); % Update number of bit errors
numBits = numBits + FRM; %Update number of bits processed
%itersHist = step(Hist, iters); % Update histogram

% Manage slot number with each subframe processed
nS = nS + 2;
nS = mod(nS, 20);
tx=[tx;t2];
rx=[rx;c0];
end

ber = numErrs/numBits; % Compute Bit Error Rate (BER)

end



function [tx,rx,ber, numBits]=channel_effect_selective(EbNo, maxNumErrs, maxNumBits,m,k,ss)

FRM=2048; % Size of bit frame
Kplus=FRM+24;
BitError = comm.ErrorRate;
AWGN = comm.AWGNChannel;
Indices = lteIntrlvrIndices(Kplus);

if k==1
    a1={'QPSK'};
    a2='QPSK';
    s.Modulation=a2;
    s.Nlayers=1;
    s.TxScheme='Port0';
    s.NIR=0;
    s.NSoftbits=0;
    s.DuplexMode='FDD';
    s.TDDConfig=0;
    
    
elseif k==2
    
    a1={'16QAM'};
    a2='16QAM';
    s.Modulation=a2;
    s.Nlayers=1;
    s.TxScheme='Port0';
    s.NIR=0;
    s.NSoftbits=0;
    s.DuplexMode='FDD';
    s.TDDConfig=0;
    
elseif k==3
    
    a1={'64QAM'};
    a2='64QAM';
    s.Modulation=a2;
    s.Nlayers=1;
    s.TxScheme='Port0';
    s.NIR=0;
    s.NSoftbits=0;
    s.DuplexMode='FDD';
    s.TDDConfig=0;
    
end


maxIter=6;
CodingRate=Kplus/(3*Kplus+12);
snr = EbNo;
noiseVar = 10.^(-snr/10);
Hist=dsp.Histogram('LowerLimit', 1, 'UpperLimit', maxIter, 'NumBins', maxIter,'RunningHistogram', true);

%xx=ceil((FRM+4)/rr);

numErrs = 0; numBits = 0; nS=0;

rx=[];
tx=[];
while ((numErrs < maxNumErrs) && (numBits < maxNumBits))
% Transmitter
u = randi([0 1], FRM,1); % Randomly generated input bits
%data= CbCRCGenerator(u); % Transport block CRC code
q = lteTurboEncode(u);

%t1=lteRateMatchTurbo(q,xx,0,s);


t2 =lteSymbolModulate(q,a1);


% Channel
g=siso_selective(t2,ss);

c0 = awgn(g,snr); % AWGN channel
% Receiver



r0 = lteSymbolDemodulate(c0,a2,'Soft');

%r1 = lteRateRecoverTurbo(r0,2400,0,s);
%a=cell2mat(r1);
%a=double(a);
y = lteTurboDecode(r0,m);
y=double(y);
% Turbo Decoder
%z=cd(y)
% Measurements
numErrs = numErrs + sum(~(y)==u); % Update number of bit errors
numBits = numBits + FRM; %Update number of bits processed
%itersHist = step(Hist, iters); % Update histogram

% Manage slot number with each subframe processed
nS = nS + 2;
nS = mod(nS, 20);
tx=[tx;t2];
rx=[rx;c0];
end

ber = numErrs/numBits; % Compute Bit Error Rate (BER)

end