EB=-5:0.5:15;
R=0.3:0.05:0.95;

eb=10.^(EB/10);



throughput_3=4*R(1,1)*((1-BER_3_QAM16).*(1-erfc(eb)));

throughput_35=4*R(1,2)*((1-BER_35_QAM16).*(1-erfc(eb)));

throughput_5=4*R(1,5)*((1-BER_5_QAM16).*(1-erfc(eb)));

throughput_6=4*R(1,7)*((1-BER_6_QAM16).*(1-erfc(eb)));

throughput_65=4*R(1,8)*((1-BER_65_QAM16).*(1-erfc(eb)));

throughput_7=4*R(1,9)*((1-BER_7_QAM16).*(1-erfc(eb)));


throughput_75=4*R(1,10)*((1-BER_75_QAM16).*(1-erfc(eb)));




plot(EB,throughput_3)

hold on
plot(EB,throughput_35)

hold on
plot(EB,throughput_5)

hold on
plot(EB,throughput_6)

hold on
plot(EB,throughput_65)

hold on
plot(EB,throughput_7)

hold on
plot(EB,throughput_75)
xlabel('EbN0(dB)')
ylabel('Throughput(bit/Hz)')
legend('r=0.3','r=0.35','r=0.5','r=0.6','r=0.65','r=0.7','r=0.75')
title('Throughput for diffrent coding rates(QAM16)')
ylim([0 3.5])

