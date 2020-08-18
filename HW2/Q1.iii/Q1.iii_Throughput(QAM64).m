EB=-5:0.5:15;
R=0.3:0.05:0.95;

eb=10.^(EB/10);

shannon_ideal_throughput=log(1+eb)/log(2);

throughput_35=6*R(1,2)*((1-BER_35_QAM64).*(1-erfc(eb)));
throughput_4=6*R(1,3)*((1-BER_35_QAM64).*(1-erfc(eb)));
throughput_5=6*R(1,5)*((1-BER_35_QAM64).*(1-erfc(eb)));
throughput_7=6*R(1,9)*((1-BER_35_QAM64).*(1-erfc(eb)));



plot(EB,throughput_35)

hold on

plot(EB,throughput_4)

hold on

plot(EB,throughput_5)

hold on

plot(EB,throughput_7)
xlabel('EbN0(dB)')
ylabel('Throughput(bit/Hz)')
legend('r=0.35','r=4','r=5','r=7')
title('Throughput for diffrent coding rates(QAM64)')
ylim([0 3.5])

