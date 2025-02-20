import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, RefreshControl, Dimensions, View } from "react-native";
import { Box } from "@/components/ui/box";
import { Button } from "@/components/ui/button";
import { ButtonText, ButtonIcon } from "@/components/ui/button";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { Heading } from "@/components/ui/heading";
import { LogOut, Package, Clock, Check, Plus, List, ChevronRight, RefreshCw, TrendingUp, DollarSign } from 'lucide-react-native';
import { Avatar } from "@/components/ui/avatar";
import { AvatarFallbackText } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { Center } from "@/components/ui/center";
import { useState, useCallback, useEffect, useMemo, memo } from 'react';
import { getOrderStats } from '@/lib/api_items';
import { router } from "expo-router";
import {
  LineChart,
  BarChart,
  PieChart,
} from "react-native-chart-kit";
import { Animated as RNAnimated } from 'react-native';
import { useRef } from 'react';

const screenWidth = Dimensions.get("window").width;

const ShimmerEffect = memo(() => {
  const translateX = useRef(new RNAnimated.Value(-100)).current;

  useEffect(() => {
    const shimmerAnimation = RNAnimated.loop(
      RNAnimated.sequence([
        RNAnimated.timing(translateX, {
          toValue: 100,
          duration: 1000,
          useNativeDriver: true,
        }),
        RNAnimated.timing(translateX, {
          toValue: -100,
          duration: 0,
          useNativeDriver: true,
        }),
      ])
    );

    shimmerAnimation.start();

    return () => shimmerAnimation.stop();
  }, [translateX]);

  return (
    <RNAnimated.View
      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
      style={[
        {
          transform: [{ translateX }],
          width: '200%',
        },
      ]}
    />
  );
});

const LoadingState = () => {
  const pulseAnim = useRef(new RNAnimated.Value(0.3)).current;

  useEffect(() => {
    const pulseAnimation = RNAnimated.loop(
      RNAnimated.sequence([
        RNAnimated.timing(pulseAnim, {
          toValue: 0.6,
          duration: 1000,
          useNativeDriver: true,
        }),
        RNAnimated.timing(pulseAnim, {
          toValue: 0.3,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );

    pulseAnimation.start();

    return () => pulseAnimation.stop();
  }, []);

  return (
    <Box className="px-4 py-4">
      {/* Header Skeleton */}
      <Box className="bg-gradient-to-br from-primary-500/20 to-primary-600/20 rounded-3xl p-6 shadow-sm mb-6 relative overflow-hidden">
        <HStack className="justify-between items-start">
          <VStack space="xs">
            <RNAnimated.View style={{ opacity: pulseAnim }}>
              <Skeleton h={4} w={100} rounded="full" startColor="primary.100" endColor="primary.200" />
            </RNAnimated.View>
            <RNAnimated.View style={{ opacity: pulseAnim }}>
              <Skeleton h={8} w={200} rounded="full" startColor="primary.100" endColor="primary.200" />
            </RNAnimated.View>
            <HStack space="sm" className="mt-1">
              <RNAnimated.View style={{ opacity: pulseAnim }}>
                <Skeleton h={6} w={80} rounded="full" startColor="primary.100" endColor="primary.200" />
              </RNAnimated.View>
              <RNAnimated.View style={{ opacity: pulseAnim }}>
                <Skeleton h={6} w={80} rounded="full" startColor="primary.100" endColor="primary.200" />
              </RNAnimated.View>
            </HStack>
          </VStack>
          <HStack space="sm">
            <RNAnimated.View style={{ opacity: pulseAnim }}>
              <Skeleton rounded="full" size="lg" startColor="primary.100" endColor="primary.200" />
            </RNAnimated.View>
          </HStack>
        </HStack>
        <ShimmerEffect />
      </Box>
      
      {/* Stats Skeletons */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        className="mb-8"
      >
        {[1, 2, 3].map((_, index) => (
          <Box 
            key={index}
            className="bg-gradient-to-br from-gray-100 to-gray-200 p-5 rounded-3xl mr-4 relative overflow-hidden"
            style={{ minWidth: 200 }}
          >
            <VStack space="md">
              <HStack className="justify-between">
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={12} w={12} rounded="xl" />
                </RNAnimated.View>
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={8} w={20} rounded="full" />
                </RNAnimated.View>
              </HStack>
              <VStack space="xs">
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={8} w={24} rounded="md" />
                </RNAnimated.View>
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={4} w={16} rounded="full" />
                </RNAnimated.View>
              </VStack>
            </VStack>
            <ShimmerEffect />
          </Box>
        ))}
      </ScrollView>
      
      {/* Chart Skeletons */}
      {[1, 2, 3].map((_, index) => (
        <Box 
          key={index}
          className="bg-white rounded-3xl p-6 shadow-sm mb-6 relative overflow-hidden"
        >
          <VStack space="md">
            <HStack className="justify-between items-center">
              <VStack>
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={6} w={120} rounded="md" />
                </RNAnimated.View>
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={4} w={80} rounded="full" className="mt-1" />
                </RNAnimated.View>
              </VStack>
              <RNAnimated.View style={{ opacity: pulseAnim }}>
                <Skeleton h={8} w={24} rounded="full" />
              </RNAnimated.View>
            </HStack>
            <Box className="bg-gray-50 rounded-2xl p-4 mt-2">
              <RNAnimated.View style={{ opacity: pulseAnim }}>
                <Skeleton h={220} rounded="lg" />
              </RNAnimated.View>
            </Box>
          </VStack>
          <ShimmerEffect />
        </Box>
      ))}
      
      {/* Quick Actions Skeleton */}
      <Box className="mb-6">
        <HStack className="justify-between items-center mb-4">
          <VStack>
            <RNAnimated.View style={{ opacity: pulseAnim }}>
              <Skeleton h={6} w={100} rounded="md" />
            </RNAnimated.View>
            <RNAnimated.View style={{ opacity: pulseAnim }}>
              <Skeleton h={4} w={80} rounded="full" className="mt-1" />
            </RNAnimated.View>
          </VStack>
          <RNAnimated.View style={{ opacity: pulseAnim }}>
            <Skeleton h={8} w={24} rounded="full" />
          </RNAnimated.View>
        </HStack>
        <HStack space="md">
          {[1, 2].map((_, index) => (
            <Box 
              key={index}
              className="flex-1 bg-gradient-to-br from-gray-100 to-gray-200 p-5 rounded-3xl relative overflow-hidden"
              style={{ height: 160 }}
            >
              <VStack space="sm">
                <RNAnimated.View style={{ opacity: pulseAnim }}>
                  <Skeleton h={12} w={12} rounded="xl" />
                </RNAnimated.View>
                <VStack space="xs" className="mt-2">
                  <RNAnimated.View style={{ opacity: pulseAnim }}>
                    <Skeleton h={6} w={24} rounded="md" />
                  </RNAnimated.View>
                  <RNAnimated.View style={{ opacity: pulseAnim }}>
                    <Skeleton h={4} w={32} rounded="full" />
                  </RNAnimated.View>
                </VStack>
              </VStack>
              <ShimmerEffect />
            </Box>
          ))}
        </HStack>
      </Box>
    </Box>
  );
};

const ChartCard = memo(({ title, subtitle, subtitleColor, children }) => (
  <RNAnimated.View 
    className="bg-white rounded-3xl p-6 shadow-lg mb-6"
  >
    <VStack space="md">
      <HStack className="justify-between items-center">
        <VStack>
          <Heading size="sm" className="text-gray-800">{title}</Heading>
          <Text className="text-gray-500 text-xs">Last 30 days performance</Text>
        </VStack>
        <Box className={`${subtitleColor} px-3 py-2 rounded-full`}>
          <HStack space="xs" className="items-center">
            <TrendingUp size={12} className={`${subtitleColor.replace('bg-', 'text-').replace('50', '600')}`} />
            <Text className={`${subtitleColor.replace('bg-', 'text-').replace('50', '600')} text-xs font-medium`}>
              {subtitle}
            </Text>
          </HStack>
        </Box>
      </HStack>
      <Box className="mt-2">
        {children}
      </Box>
    </VStack>
  </RNAnimated.View>
));

const StatsCard = memo(({ stat }) => (
  <Card
    className={`${stat.color} p-5 rounded-3xl shadow-lg mx-2 first:ml-0 last:mr-0`}
    style={{ 
      minWidth: 200,
      transform: [{ translateY: 0 }],
      elevation: 8,
    }}
  >
    <VStack space="md">
      <HStack className="items-center justify-between">
        <Box className="bg-white/25 p-4 rounded-2xl backdrop-blur-lg">
          <stat.icon size={24} color="white" strokeWidth={2.5} />
        </Box>
        <Box className={`${stat.trendUp ? 'bg-white/30' : 'bg-white/20'} px-3 py-2 rounded-full backdrop-blur-lg`}>
          <HStack space="xs" className="items-center">
            <TrendingUp 
              size={14} 
              color="white" 
              style={{ 
                transform: [{ rotate: stat.trendUp ? '0deg' : '180deg' }] 
              }} 
            />
            <Text className="text-white text-xs font-semibold">
              {stat.trend}
            </Text>
          </HStack>
        </Box>
      </HStack>
      <VStack space="xs">
        <Text className="text-white text-4xl font-bold tracking-tight">
          {stat.value}
        </Text>
        <Text className="text-white/90 text-sm font-medium">
          {stat.title}
        </Text>
      </VStack>
    </VStack>
  </Card>
));

const QuickActionCard = memo(({ action }) => (
  <RNAnimated.View
    style={{ flex: 1 }}
  >
    <Button
      size="lg"
      variant={action.primary ? "solid" : "outline"}
      action={action.primary ? "primary" : "secondary"}
      className={`
        ${action.primary ? 'bg-gradient-to-br from-primary-500 to-primary-600' : 'bg-white'} 
        p-5 rounded-3xl shadow-lg mx-2 first:ml-0 last:mr-0
      `}
      style={{
        height: 160,
        shadowColor: action.primary ? '#FFA001' : '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: action.primary ? 0.3 : 0.1,
        shadowRadius: 8,
        elevation: 5,
      }}
      onPress={action.onPress}
    >
      <VStack space="sm" className="items-start w-full">
        <Box 
          className={`
            p-3 rounded-xl 
            ${action.primary ? 'bg-white/20 backdrop-blur-lg' : 'bg-primary-50'}
          `}
        >
          <action.icon 
            size={26} 
            color={action.primary ? "#fff" : "#FFA001"} 
            strokeWidth={2.5}
          />
        </Box>
        <VStack space="xs" className="mt-2">
          <ButtonText 
            className={`
              text-lg font-semibold 
              ${action.primary ? 'text-white' : 'text-gray-900'}
            `}
          >
            {action.title}
          </ButtonText>
          <Text 
            className={`
              text-sm 
              ${action.primary ? 'text-white/80' : 'text-gray-500'}
            `}
          >
            {action.description}
          </Text>
        </VStack>
      </VStack>
    </Button>
  </RNAnimated.View>
));

const Home = () => {
  const { user, logout, loading } = useAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [orderStats, setOrderStats] = useState({
    total: 150,
    pending: 25,
    completed: 125
  });
  const [statsLoading, setStatsLoading] = useState(true);

  // Dummy data for charts
  const chartData = useMemo(() => ({
    monthlyData: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [
        {
          data: [20, 45, 28, 80, 99, 43],
          color: (opacity = 1) => `rgba(255, 160, 1, ${opacity})`, // primary color
          strokeWidth: 2
        }
      ],
    },
    orderTypeData: [
      {
        name: "Regular",
        orders: 45,
        color: "#FF6384",
        legendFontColor: "#7F7F7F",
        legendFontSize: 12
      },
      {
        name: "Express",
        orders: 25,
        color: "#36A2EB",
        legendFontColor: "#7F7F7F",
        legendFontSize: 12
      },
      {
        name: "Priority",
        orders: 30,
        color: "#FFCE56",
        legendFontColor: "#7F7F7F",
        legendFontSize: 12
      }
    ],
    dailyOrdersData: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      datasets: [
        {
          data: [15, 12, 18, 25, 22, 20, 10]
        }
      ]
    }
  }), []);

  const fetchStats = async () => {
    try {
      setStatsLoading(true);
      const stats = await getOrderStats();
      setOrderStats(stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const chartConfig = useMemo(() => ({
    backgroundGradientFrom: "#ffffff",
    backgroundGradientTo: "#ffffff",
    color: (opacity = 1) => `rgba(255, 160, 1, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.8,
    useShadowColorFromDataset: false,
    decimalPlaces: 0,
    propsForLabels: {
      fontSize: 11,
      fontFamily: 'System',
      fontWeight: '500',
      color: '#64748b',
    },
    propsForBackgroundLines: {
      strokeDasharray: "6 6",
      stroke: "#f1f5f9",
      strokeWidth: 1,
    },
    fillShadowGradient: "#FFA001",
    fillShadowGradientOpacity: 0.3,
    labelColor: (opacity = 1) => `rgba(100, 116, 139, ${opacity})`,
  }), []);

  const stats = [
    { 
      title: "Total Orders", 
      value: statsLoading ? <RefreshCw className="animate-spin" size={20} color="white" /> : orderStats.total.toString(), 
      color: "bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700",
      icon: Package,
      trend: "+12.5%",
      trendUp: true
    },
    { 
      title: "Pending Orders", 
      value: statsLoading ? <RefreshCw className="animate-spin" size={20} color="white" /> : orderStats.pending.toString(),
      color: "bg-gradient-to-br from-warning-500 via-warning-600 to-warning-700",
      icon: Clock,
      trend: "+5.2%",
      trendUp: true
    },
    { 
      title: "Total Revenue", 
      value: statsLoading ? <RefreshCw className="animate-spin" size={20} color="white" /> : "$12,450",
      color: "bg-gradient-to-br from-success-500 via-success-600 to-success-700",
      icon: DollarSign,
      trend: "+8.1%",
      trendUp: true
    },
  ];

  const quickActions = [
    { 
      title: "Create Order", 
      icon: Plus, 
      primary: true,
      onPress: () => router.push('/create-order'),
      description: "Create a new customer order",
    },
    { 
      title: "View Orders", 
      icon: List, 
      primary: false,
      onPress: () => router.push('/send-orders'),
      description: "Check order history",
    },
  ];

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchStats();
    setRefreshing(false);
  }, []);

  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) {
    return (
      <SafeAreaView className="flex-1 bg-gray-50">
        <LoadingState />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView 
        className="flex-1"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        <Box className="px-4 py-4">
          {/* Enhanced Header Section */}
          <Box
            className="bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 rounded-3xl p-6 shadow-xl mb-6"
          >
            <VStack space="md">
              <HStack className="justify-between items-start">
                <VStack space="xs">
                  <Text className="text-white/90 text-base font-medium">
                    {getTimeOfDay()},
                  </Text>
                  <Heading size="xl" className="text-white">
                    {user?.employee_name || user?.user_name || 'User'}
                  </Heading>
                  <HStack space="sm" className="items-center mt-1">
                    <Box className="bg-white/20 px-3 py-1 rounded-full">
                      <Text className="text-white/90 text-xs">
                        Terminal: {user?.terminal || 'N/A'}
                      </Text>
                    </Box>
                    <Box className="bg-white/20 px-3 py-1 rounded-full">
                      <Text className="text-white/90 text-xs">
                        ID: {user?.user_id || 'N/A'}
                      </Text>
                    </Box>
                  </HStack>
                </VStack>
                <HStack space="sm">
                  <Avatar 
                    size="lg" 
                    className="bg-white/20 border-2 border-white/30"
                    style={{
                      shadowColor: '#000',
                      shadowOffset: { width: 0, height: 4 },
                      shadowOpacity: 0.2,
                      shadowRadius: 8,
                      elevation: 5,
                    }}
                  >
                    <AvatarFallbackText className="text-white">
                      {getInitials(user?.employee_name || 'User')}
                    </AvatarFallbackText>
                  </Avatar>
                  <Button
                    variant="solid"
                    size="sm"
                    onPress={logout}
                    className="bg-white/20 border border-white/30 self-start mt-1"
                  >
                    <ButtonIcon as={LogOut} size={18} className="text-white" />
                  </Button>
                </HStack>
              </HStack>

              <HStack className="justify-between items-center mt-4 bg-white/10 p-4 rounded-2xl backdrop-blur-lg">
                <VStack>
                  <Text className="text-white/80 text-xs">Business ID</Text>
                  <Text className="text-white font-bold">{user?.businessId || 'N/A'}</Text>
                </VStack>
                <Box className="w-[1px] h-8 bg-white/20" />
                <VStack>
                  <Text className="text-white/80 text-xs">Role</Text>
                  <Text className="text-white font-bold capitalize">{user?.is_admin || 'User'}</Text>
                </VStack>
                <Box className="w-[1px] h-8 bg-white/20" />
                <VStack>
                  <Text className="text-white/80 text-xs">Status</Text>
                  <Text className="text-white font-bold capitalize">{user?.status || 'N/A'}</Text>
                </VStack>
              </HStack>
            </VStack>
          </Box>

          {/* Stats Section with enhanced spacing and animations */}
          <VStack space="lg" className="mb-8">
            <HStack className="justify-between items-center mb-4">
              <VStack>
                <Heading size="sm" className="text-gray-800">Dashboard Overview</Heading>
                <Text className="text-gray-500 text-xs">Today's business summary</Text>
              </VStack>
              <Button
                variant="outline"
                size="sm"
                onPress={fetchStats}
                className="border-primary-100 bg-primary-50"
              >
                <HStack space="xs" className="items-center px-1">
                  <RefreshCw size={14} className="text-primary-500" />
                  <ButtonText className="text-primary-500 text-sm">Refresh</ButtonText>
                </HStack>
              </Button>
            </HStack>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              className="py-2"
              contentContainerStyle={{
                paddingRight: 16,
              }}
            >
              {stats.map((stat, index) => (
                <RNAnimated.View
                  key={index}
                  className="first:ml-0"
                >
                  <StatsCard stat={stat} />
                </RNAnimated.View>
              ))}
            </ScrollView>
          </VStack>

          {/* Charts Section */}
          <VStack space="lg" className="mb-8">
            <Heading size="sm" className="text-gray-800 mb-2">Analytics</Heading>
            
            {/* Monthly Orders Chart */}
            <ChartCard 
              title="Monthly Orders" 
              subtitle="+23.5% vs last month"
              subtitleColor="bg-primary-50"
            >
              <Box className="rounded-2xl overflow-hidden bg-gray-50/50 p-4">
                <LineChart
                  data={chartData.monthlyData}
                  width={screenWidth - 64}
                  height={220}
                  chartConfig={{
                    ...chartConfig,
                    propsForDots: {
                      r: "4",
                      stroke: "#FFA001",
                      strokeWidth: "2",
                      fill: "#fff"
                    }
                  }}
                  bezier
                  style={{
                    borderRadius: 16
                  }}
                  withHorizontalLines={true}
                  withVerticalLines={false}
                  withDots={true}
                  withShadow={true}
                  segments={5}
                  withInnerLines={true}
                  getDotColor={() => "#FFA001"}
                />
              </Box>
            </ChartCard>

            {/* Order Type Distribution */}
            <ChartCard 
              title="Order Distribution" 
              subtitle="Well balanced"
              subtitleColor="bg-success-50"
            >
              <Box className="rounded-2xl overflow-hidden bg-gray-50/50 p-4">
                <PieChart
                  data={chartData.orderTypeData}
                  width={screenWidth - 64}
                  height={220}
                  chartConfig={chartConfig}
                  accessor={"orders"}
                  backgroundColor={"transparent"}
                  paddingLeft={"15"}
                  center={[10, 0]}
                  absolute
                  hasLegend={true}
                  avoidFalseZero={true}
                />
              </Box>
            </ChartCard>

            {/* Daily Orders Chart */}
            <ChartCard 
              title="Daily Performance" 
              subtitle="Peak on Thursday"
              subtitleColor="bg-warning-50"
            >
              <Box className="rounded-2xl overflow-hidden bg-gray-50/50 p-4">
                <BarChart
                  data={chartData.dailyOrdersData}
                  width={screenWidth - 64}
                  height={220}
                  chartConfig={{
                    ...chartConfig,
                    barPercentage: 0.7,
                  }}
                  style={{
                    borderRadius: 16
                  }}
                  showBarTops={true}
                  showValuesOnTopOfBars={true}
                  fromZero={true}
                  withInnerLines={true}
                  segments={5}
                />
              </Box>
            </ChartCard>
          </VStack>

          {/* Quick Actions */}
          <VStack space="md" className="mb-6">
            <HStack className="justify-between items-center mb-4">
              <VStack>
                <Heading size="sm" className="text-gray-800">Quick Actions</Heading>
                <Text className="text-gray-500 text-xs">Fast access to common tasks</Text>
              </VStack>
              <Button
                variant="link"
                size="sm"
                className="items-center"
              >
                <HStack space="xs" className="items-center">
                  <Text className="text-primary-500 text-sm">View All</Text>
                  <ChevronRight size={16} className="text-primary-500" />
                </HStack>
              </Button>
            </HStack>
            <HStack>
              {quickActions.map((action, index) => (
                <QuickActionCard key={index} action={action} />
              ))}
            </HStack>
          </VStack>
        </Box>
      </ScrollView>
    </SafeAreaView>
  );
};

export default memo(Home);
