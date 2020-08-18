EB=-5:0.5:15;
R=0.3:0.05:0.95;

eb=10.^(EB/10);



throughput_3=2*R(1,1)*((1-BER_3_QPSK).*(1-erfc(eb)));

throughput_35=2*R(1,2)*((1-BER_35_QPSK).*(1-erfc(eb)));
throughput_4=2*R(1,3)*((1-BER_4_QPSK).*(1-erfc(eb)));
throughput_45=2*R(1,4)*((1-BER_45_QPSK).*(1-erfc(eb)));
throughput_5=2*R(1,5)*((1-BER_5_QPSK).*(1-erfc(eb)));
throughput_55=2*R(1,6)*((1-BER_55_QPSK).*(1-erfc(eb)));
throughput_6=2*R(1,7)*((1-BER_6_QPSK).*(1-erfc(eb)));
throughput_65=2*R(1,8)*((1-BER_65_QPSK).*(1-erfc(eb)));
throughput_7=2*R(1,9)*((1-BER_7_QPSK).*(1-erfc(eb)));
throughput_75=2*R(1,10)*((1-BER_75_QPSK).*(1-erfc(eb)));
throughput_8=2*R(1,11)*((1-BER_8_QPSK).*(1-erfc(eb)));
throughput_85=2*R(1,12)*((1-BER_85_QPSK).*(1-erfc(eb)));




plot(EB,throughput_3)

hold on
plot(EB,throughput_35)

hold on
plot(EB,throughput_4)

hold on
plot(EB,throughput_45)

hold on
plot(EB,throughput_5)

hold on
plot(EB,throughput_55)

hold on
plot(EB,throughput_6)

hold on
plot(EB,throughput_65)

hold on
plot(EB,throughput_7)

hold on
plot(EB,throughput_75)

hold on
plot(EB,throughput_8)

hold on
plot(EB,throughput_85)
xlabel('EbN0(dB)')
ylabel('Throughput(bit/Hz)')
legend('r=0.3','r=0.35','r=0.4','r=0.45','r=0.5','r=0.55','r=0.6','r=0.65','r=0.7','r=0.75','r=0.8','r=0.85')
title('Throughput for diffrent coding rates(QPSK)')
ylim([0 5])

